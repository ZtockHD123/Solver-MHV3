import sqlite3
import json
from collections import defaultdict

# --- CONFIGURACIÓN ---
DB_FILE = './BD/resultados.db'

TABLA_INSTANCIAS = 'instancias'
TABLA_EXPERIMENTOS = 'experimentos'
# ---------------------

def ejecutar_consulta(cursor, query, params=None):
    """Ejecuta una consulta y devuelve todos los resultados."""
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    return cursor.fetchall()

def aplanar_lista(lista_de_tuplas):
    """Convierte [('a',), ('b',)] a ['a', 'b']."""
    return [item[0] for item in lista_de_tuplas]

def analizar_base_de_datos(db_path):
    """
    Se conecta a la base de datos, extrae la configuración de los experimentos
    y la imprime en formato JSON, basado en el esquema confirmado.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Conectado exitosamente a la base de datos: {db_path}\n")

        # 1. Obtener los tipos de problemas (uniendo con la tabla de instancias)
        print("1. Identificando tipos de problemas...")
        query = f"""
            SELECT DISTINCT i.tipo_problema
            FROM {TABLA_EXPERIMENTOS} e
            JOIN {TABLA_INSTANCIAS} i ON e.fk_id_instancia = i.id_instancia
        """
        problemas_raw = ejecutar_consulta(cursor, query)
        tipos_de_problema = aplanar_lista(problemas_raw)
        print(f"   -> Problemas encontrados: {tipos_de_problema}")

        # 2. Obtener las metaheurísticas (mhs)
        print("2. Identificando Metaheurísticas (mhs)...")
        mhs_raw = ejecutar_consulta(cursor, f"SELECT DISTINCT MH FROM {TABLA_EXPERIMENTOS}")
        mhs = sorted(aplanar_lista(mhs_raw))
        print(f"   -> MHs encontradas: {mhs}")

        # 3. Obtener los esquemas de binarización (DS_actions)
        print("3. Identificando esquemas de binarización (DS_actions)...")
        ds_actions_raw = ejecutar_consulta(cursor, f"SELECT DISTINCT binarizacion FROM {TABLA_EXPERIMENTOS} WHERE binarizacion IS NOT NULL AND binarizacion != 'N/A'")
        ds_actions = sorted(aplanar_lista(ds_actions_raw))
        print(f"   -> Binarizaciones encontradas: {ds_actions}")

        # 4. Obtener instancias y dimensiones
        print("4. Extrayendo instancias y dimensiones...")
        instancias = defaultdict(list)
        dimensiones_ben = defaultdict(list)
        for prob in tipos_de_problema:
            query = f"""
                SELECT DISTINCT i.nombre
                FROM {TABLA_EXPERIMENTOS} e
                JOIN {TABLA_INSTANCIAS} i ON e.fk_id_instancia = i.id_instancia
                WHERE i.tipo_problema = ?
            """
            nombres_instancias_raw = ejecutar_consulta(cursor, query, (prob,))
            nombres_instancias = sorted(aplanar_lista(nombres_instancias_raw))
            
            if prob == 'BEN':
                # Para BEN, el nombre del experimento en la tabla incluye la dimensión
                exp_nombres_raw = ejecutar_consulta(cursor, f"SELECT DISTINCT experimento FROM {TABLA_EXPERIMENTOS} WHERE experimento LIKE '% %'")
                exp_nombres = aplanar_lista(exp_nombres_raw)
                
                funciones_ben_usadas = set()
                for nombre_completo in exp_nombres:
                    partes = nombre_completo.split()
                    if len(partes) == 2:
                        funcion, dim = partes
                        funciones_ben_usadas.add(funcion)
                        if int(dim) not in dimensiones_ben[funcion]:
                            dimensiones_ben[funcion].append(int(dim))
                instancias['BEN'] = sorted(list(funciones_ben_usadas))

            else: # SCP, USCP, KP
                instancias[prob] = nombres_instancias
        
        print("   -> Instancias extraídas.")

        # 5. Obtener parámetros (iteraciones, poblacion, num_experimentos)
        print("5. Reconstruyendo parámetros de experimentos...")
        experimentos_params = {}
        for prob in tipos_de_problema:
            params = {}
            # Obtener iter y pop desde el primer experimento encontrado para ese problema
            query = f"""
                SELECT e.paramMH
                FROM {TABLA_EXPERIMENTOS} e
                JOIN {TABLA_INSTANCIAS} i ON e.fk_id_instancia = i.id_instancia
                WHERE i.tipo_problema = ? LIMIT 1
            """
            param_mh_raw = ejecutar_consulta(cursor, query, (prob,))
            if param_mh_raw:
                param_mh_str = param_mh_raw[0][0]
                partes = param_mh_str.split(',')
                for parte in partes:
                    if ':' in parte:
                        key, val = parte.split(':', 1)
                        if key.strip() == 'iter':
                            params['iteraciones'] = int(val)
                        elif key.strip() == 'pop':
                            params['poblacion'] = int(val)
            
            # --- LÓGICA DEFINITIVA PARA num_experimentos ---
            # Contar cuántas filas duplicadas de 'experimentos' hay para una misma configuración
            query = f"""
                SELECT COUNT(*)
                FROM {TABLA_EXPERIMENTOS} e
                JOIN {TABLA_INSTANCIAS} i ON e.fk_id_instancia = i.id_instancia
                WHERE i.tipo_problema = ?
                GROUP BY e.experimento, e.MH, e.binarizacion, e.paramMH, e.fk_id_instancia
                ORDER BY COUNT(*) DESC
                LIMIT 1
            """
            num_exp_raw = ejecutar_consulta(cursor, query, (prob,))
            params['num_experimentos'] = num_exp_raw[0][0] if num_exp_raw else 1
            
            experimentos_params[prob] = params
            print(f"   -> Parámetros para '{prob}': {params}")

        # 6. Construir el diccionario final
        config_reconstruida = {
            "_comentarios": {
                "ben": "Indica si se van a procesar funciones BEN.",
                "scp": "Indica si se van a procesar instancias SCP.",
                "uscp": "Indica si se van a procesar instancias USCP.",
                "kp": "Indica si se van a procesar instancias de KP.",
                "mhs": "Lista de metaheurísticas que se van a procesar.",
                "DS_actions": "Lista de acciones de binarización de la población.",
                "dimensiones": "Mapea cada función BEN a las dimensiones que utiliza.",
                "experimentos": "Parámetros globales de iteraciones y población para cada problema.",
                "instancias": "Identificadores de los instancias de los problemas que se van a procesar."
            },
            "ben": "BEN" in tipos_de_problema,
            "scp": "SCP" in tipos_de_problema,
            "uscp": "USCP" in tipos_de_problema,
            "kp": "KP" in tipos_de_problema,
            "mhs": mhs,
            "DS_actions": ds_actions,
            "dimensiones": {"BEN": dict(sorted(dimensiones_ben.items()))},
            "experimentos": dict(sorted(experimentos_params.items())),
            "instancias": dict(sorted(instancias.items()))
        }
        
        # 7. Imprimir el resultado en formato JSON
        print("\n" + "=" * 55)
        print("--- CONFIGURACIÓN RECONSTRUIDA (VERSIÓN DEFINITIVA) ---")
        print("=" * 55 + "\n")
        print("Copia y pega el siguiente texto en tu archivo 'experiments_config.json':\n")
        print(json.dumps(config_reconstruida, indent=4, ensure_ascii=False))

    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("\nConexión a la base de datos cerrada.")

if __name__ == '__main__':
    analizar_base_de_datos(DB_FILE)