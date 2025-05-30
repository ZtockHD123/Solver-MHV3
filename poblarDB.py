import os
import opfunu.cec_based

from BD.sqlite import BD
from Util.log import resumen_experimentos
from Util.util import cargar_configuracion

from crearBD import crear_BD

config = cargar_configuracion('util/json/experiments_config.json')

bd = BD()
dimensiones_cache = {}

'''
DS_lista = [
    'V1-STD', 'V1-COM', 'V1-PS', 'V1-ELIT',
    'V2-STD', 'V2-COM', 'V2-PS', 'V2-ELIT',
    'V3-STD', 'V3-COM', 'V3-PS', 'V3-ELIT',
    'V4-STD', 'V4-COM', 'V4-PS', 'V4-ELIT',
    'S1-STD', 'S1-COM', 'S1-PS', 'S1-ELIT',
    'S2-STD', 'S2-COM', 'S2-PS', 'S2-ELIT',
    'S3-STD', 'S3-COM', 'S3-PS', 'S3-ELIT',
    'S4-STD', 'S4-COM', 'S4-PS', 'S4-ELIT',
]
'''

if __name__ == '__main__':
    crear_BD()

def obtener_dimensiones_ben(funcion):
    for key, dims in config['dimensiones']['BEN'].items():
        if funcion in key.split("-"):
            return dims
    
    if funcion in bd.opfunu_cec_data:
        func_class = getattr(opfunu.cec_based, f"{funcion}")
        return [func_class().dim_default]
    
    raise ValueError(f"La función '{funcion}' no está definida en la configuración de dimensiones ni en opfunu.")

def obtener_dimensiones(instance, problema):
    if (instance, problema) in dimensiones_cache:
        return dimensiones_cache[(instance, problema)]
    
    directorios = {
        'SCP': './Problem/SCP/Instances/',
        'USCP': './Problem/USCP/Instances/',
        'KP': './Problem/KP/Instances/' 
    }

    if problema in directorios:
        ruta_instancia = ""
        if problema == 'SCP':
            prefijo = 'scp'
            ruta_instancia = os.path.join(directorios[problema], f"{prefijo}{instance}.txt")
        elif problema == 'USCP':
            if instance.startswith('u'): # Asumiendo que a veces viene con 'u' de más
                instance_name_for_file = instance[1:]
            else:
                instance_name_for_file = instance
            prefijo = 'uscp'
            ruta_instancia = os.path.join(directorios[problema], f"{prefijo}{instance_name_for_file}.txt")
        elif problema == 'KP':
            # Para KP, los nombres de archivo son directos y usualmente tienen extensión .txt o ninguna si así los guardaste.
            # El archivo problem.py para KP que me diste abre './Problem/KP/Instances/'+instance (sin .txt)
            # Ajusta la extensión si es necesario. Si tus archivos KP *sí* tienen .txt, añade ".txt" aquí.
            ruta_instancia = os.path.join(directorios[problema], instance) # Asumiendo que 'instance' ya es el nombre completo del archivo
            # Si los archivos de instancia KP en config.json no tienen extensión y los archivos reales sí:
            # ruta_instancia = os.path.join(directorios[problema], f"{instance}.txt")

        if not os.path.exists(ruta_instancia):
            # Intenta con extensión .txt si no se encontró y es KP (ya que SCP/USCP la añaden)
            if problema == 'KP' and not ruta_instancia.endswith(".txt"):
                ruta_instancia_txt = ruta_instancia + ".txt"
                if os.path.exists(ruta_instancia_txt):
                    ruta_instancia = ruta_instancia_txt
                else:
                    raise FileNotFoundError(f"Archivo KP {ruta_instancia} (o {ruta_instancia_txt}) no encontrado.")
            else:
                raise FileNotFoundError(f"Archivo {ruta_instancia} no encontrado.")

        with open(ruta_instancia, 'r') as file:
            if problema == 'SCP' or problema == 'USCP':
                line = file.readline().strip()
                filas, columnas = map(int, line.split())
                dimensiones = f"{filas} x {columnas}"
            elif problema == 'KP':
                line = file.readline().strip() # Primera línea: items capacity
                num_items, capacity = map(float, line.split()) # O int si son siempre enteros
                num_items = int(num_items) # Generalmente num_items es entero
                dimensiones = f"{num_items} items, Cap: {capacity}" # O solo el número de items
                                                                    # ej: f"{num_items} items"
        dimensiones_cache[(instance, problema)] = dimensiones
        return dimensiones

    return "-"

def crear_data_experimento(instancia, dim, mh, binarizacion, iteraciones, poblacion, extra_params, problemaActual):
    nombre_experimento = ""
    instance_tuple = instancia[0]
    if problemaActual == 'BEN':
        nombre_experimento = f'{instance_tuple[1]} {dim}' # Para BEN, dim_ben es la dimensión real
    else: # SCP, USCP, KP
        nombre_experimento = f'{instance_tuple[1]}' # Para otros, es solo el nombre de la instancia

    return {
        'experimento': nombre_experimento,
        'MH': mh,
        'binarizacion': binarizacion if binarizacion else 'N/A',
        'paramMH': f'iter:{iteraciones},pop:{poblacion}{extra_params}',
        'ML': '',
        'paramML': '',
        'ML_FS': '',
        'paramML_FS': '',
        'estado': 'pendiente'
    }

def crear_resumen_log(instancia, dim, mh, binarizacion, iteraciones, poblacion, extra_params, problemaActual, num_experimentos=1):
 # 'instancia' es la lista que se le pasa, ej: [(id_real, 'nombre_real_instancia', ...)]
    # El nombre real de la instancia está en el segundo elemento de la tupla,
    # y esa tupla es el primer (y único) elemento de la lista 'instancia'.
    nombre_real_de_la_instancia = instancia[0][1]

    # Ahora llamamos a obtener_dimensiones con el nombre correcto
    dimensiones_instancia = obtener_dimensiones(nombre_real_de_la_instancia, problemaActual)

    return {
        "Problema": problemaActual,
        "Instancia": nombre_real_de_la_instancia,  # Usamos el nombre que extrajimos
        "Dimensión": dimensiones_instancia if problemaActual != 'BEN' else dim,
        "MH": mh,
        "Iteraciones": iteraciones,
        "Población": poblacion,
        "Binarización": binarizacion if binarizacion else 'N/A',
        "Extra Params": extra_params,
        "Total Experimentos": num_experimentos
    }

def insertar_experimentos(instancias, dimensiones, mhs, num_experimentos, iteraciones, poblacion, problemaActual, extra_params=""):
    global cantidad, log_resumen

    for dim_parametro_ben in dimensiones: # Renombrar 'dim' para evitar confusión
        for mh in mhs:
            # Verifica si el problema actual requiere binarización
            if problemaActual in ['SCP', 'USCP', 'KP']: # Añadir 'KP'
                for binarizacion in config['DS_actions']:  # Solo iterar si el problema es discreto
                    # Para SCP/USCP/KP, dim_parametro_ben no se usa directamente para data['experimento'],
                    # la dimensión real se obtiene de la instancia.
                    
                    data = crear_data_experimento(instancias, dim_parametro_ben, mh, binarizacion, iteraciones, poblacion, extra_params, problemaActual)
                    id_de_la_instancia_actual = instancias[0][0]
                    bd.insertarExperimentos(data, num_experimentos, id_de_la_instancia_actual)
                    cantidad += num_experimentos
                    log_resumen.append(crear_resumen_log(instancias, dim_parametro_ben, mh, binarizacion, iteraciones, poblacion, extra_params, problemaActual, num_experimentos))
            else: # BEN
                data = crear_data_experimento(instancias, dim_parametro_ben, mh, None, iteraciones, poblacion, extra_params, problemaActual)
                bd.insertarExperimentos(data, num_experimentos, instancias[0])
                cantidad += num_experimentos
                log_resumen.append(crear_resumen_log(instancias, dim_parametro_ben, mh, None, iteraciones, poblacion, extra_params, problemaActual, num_experimentos))

def agregar_experimentos():
    if config.get('ben', False):
        iteraciones = config['experimentos']['BEN']['iteraciones']
        poblacion = config['experimentos']['BEN']['poblacion']
        num_experimentos = config['experimentos']['BEN']['num_experimentos']

        for funcion in config['instancias']['BEN']:
            instancias_ben = bd.obtenerInstancias(f'''"{funcion}"''') # 'instancias' renombrado para evitar conflicto
            dimensiones_ben = obtener_dimensiones_ben(funcion)
            insertar_experimentos(instancias_ben, dimensiones_ben, config['mhs'], num_experimentos, iteraciones, poblacion, problemaActual='BEN')

    # Modificación para incluir KP junto con SCP y USCP
    for problema, activar in [('SCP', config.get('scp', False)),('USCP', config.get('uscp', False)),('KP', config.get('kp', False))]:
        if activar:
            instancias_problema_actual_nombres = config['instancias'][problema] # Nombres de instancia desde config
            # Obtener los IDs de instancia de la BD
            instancias_db = bd.obtenerInstancias(",".join(f'"{i}"' for i in instancias_problema_actual_nombres))

            iteraciones = config['experimentos'][problema]['iteraciones']
            poblacion = config['experimentos'][problema]['poblacion']
            num_experimentos = config['experimentos'][problema]['num_experimentos']

            for instancia_db_tupla in instancias_db: # instancia_db_tupla es (id_instancia, nombre_instancia, ...)
                # Para SCP y USCP, se pasaba [1] como 'dimensiones' porque la dimensión real se obtiene de la instancia.
                # Hacemos lo mismo para KP. La dimensión 'dim_parametro_ben' en insertar_experimentos no se usa
                # directamente para formar data['experimento'] para estos problemas.
                dimension_placeholder = [1] 

                # Definir extra_params específicamente para cada problema si es necesario
                extra_params = ""
                if problema in ['SCP', 'USCP']:
                    extra_params = f',repair:complex,cros:0.4;mut:0.50' # Ejemplo para SCP/USCP
                elif problema == 'KP':
                    # KP usa 'param' para GA en solverKP.py, ej: "cross:0.8;muta:0.1"
                    # Si no usas GA o no quieres parámetros fijos aquí, puede ser ""
                    # o podrías definirlo en config['experimentos']['KP']['extra_params']
                    # y leerlo.
                    # Ejemplo:
                    if 'extra_params' in config['experimentos'][problema]:
                        extra_params_config = config['experimentos'][problema]['extra_params']
                        extra_params = "".join([f',{k}:{v}' for k, v in extra_params_config.items()])
                    else:
                        extra_params = f',cross:0.8;muta:0.1' # Parámetros por defecto para GA en KP


                # 'insertar_experimentos' espera una lista de tuplas de instancia.
                # Pasamos la tupla actual dentro de una lista.
                insertar_experimentos([instancia_db_tupla], dimension_placeholder, config['mhs'], num_experimentos, iteraciones, poblacion, problemaActual=problema, extra_params=extra_params)
                
# Resumen final
if __name__ == '__main__':
    log_resumen = []
    cantidad = 0
    
    agregar_experimentos()
    resumen_experimentos(log_resumen, cantidad)