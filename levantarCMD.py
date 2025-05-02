import subprocess
import os
import sys
import platform

def abrir_cmds_ejecutar_main(num_cmds):
    # Obtener la ruta actual del script
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    programa = 'main.py'
    
    # Verificar si main.py existe en la ruta actual
    main_py_path = os.path.join(ruta_actual, programa)
    if not os.path.isfile(main_py_path):
        print(f"No se encontró {programa} en la ruta: {ruta_actual}")
        return
    
    # Verificar si Python está disponible en el sistema
    python_executable = sys.executable
    if not os.path.isfile(python_executable):
        print(f"No se encontró el ejecutable de Python en la ruta: {python_executable}")
        return

    # Determinar el sistema operativo
    sistema = platform.system()
    
    if sistema == "Windows":
        comando_base = f'start cmd /K "cd /d {ruta_actual} && {python_executable} {programa}"'
    elif sistema == "Linux":
        comando_base = f'gnome-terminal -- bash -c "cd {ruta_actual} && {python_executable} {programa}; exec bash"'
        if subprocess.call("which gnome-terminal", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
            comando_base = f'xterm -hold -e "{python_executable} {programa}"'
    else:
        print(f"El sistema operativo {sistema} no es compatible con este script.")
        return
    
    for _ in range(num_cmds):
        try:
            subprocess.Popen(comando_base, shell=True)
        except Exception as e:
            print(f"Error al intentar abrir la ventana de terminal: {e}")
            return

    print(f"Se han abierto {num_cmds} terminales ejecutando {programa} en la ruta: {ruta_actual}")

if __name__ == "__main__":
    # Definir la cantidad de terminales a levantar
    num_cmds = 10
    abrir_cmds_ejecutar_main(num_cmds)
