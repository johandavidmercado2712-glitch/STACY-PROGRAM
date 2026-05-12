import sys
import subprocess
import os

def get_history_zsh():
    histfile = os.path.expanduser("~/.zsh_history")
    if os.path.exists(histfile):
        with open(histfile, "r", errors="ignore") as f:
            lines = f.readlines()
            comandos = []
            for linea in lines[-11:]:
                if ';' in linea:
                    comando = linea.split(';', 1)[1].strip()
                    comandos.append(comando)
            return comandos
    return []

if not sys.stdin.isatty():
    stdin_data = sys.stdin.read()
    if stdin_data.strip():
        historial = stdin_data.splitlines()
        print("--- Comandos recibidos de la sesión actual (via pipe) ---")
        for linea in historial[-11:]:
            print(f"> {linea.strip()}")
    else:
        result = subprocess.run(['fc -l -11'], capture_output=True, text=True, shell=True)
        if result.stdout.strip():
            historial = result.stdout.splitlines()
            print("--- Comandos de la sesión actual (zsh fc) ---")
            for linea in historial:
                print(f"> {linea.strip()}")
        else:
            historial = get_history_zsh()
            print("--- Comandos del archivo .zsh_history ---")
            for linea in historial:
                print(f"> {linea.strip()}")
else:
    result = subprocess.run(['fc -l -11'], capture_output=True, text=True, shell=True)
    if result.stdout.strip():
        historial = result.stdout.splitlines()
        print("--- Comandos de la sesión actual (zsh fc) ---")
        for linea in historial:
            print(f"> {linea.strip()}")
    else:
        historial = get_history_zsh()
        print("--- Comandos del archivo .zsh_history ---")
        for linea in historial:
            print(f"> {linea.strip()}")