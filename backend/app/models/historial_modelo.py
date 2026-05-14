import os
import sys
import subprocess

class HistorialModelo: # muestra el historial de comandos del usuario dependiendo de su sistema operativo y tienen limite de 11 comandos 
    def obtener_desde_archivo(self):
        histfile = os.path.expanduser("~/.zsh_history")
        if os.path.exists(histfile):
            with open(histfile, "r", errors="ignore") as f:
                lines = f.readlines()
                return [l.split(';', 1)[1].strip() for l in lines[-11:] if ';' in l]
        return []

    def obtener_desde_fc(self):
        result = subprocess.run(['fc -l -11'], capture_output=True, text=True, shell=True)
        return result.stdout.splitlines() if result.stdout.strip() else []


    
class HistorialModeloCompleto: #Muestra todo el historial de comandos del usuario sin limites 
    def obtener_todo_desde_archivo(self):
        histfile = os.path.expanduser("~/.zsh_history")
        if os.path.exists(histfile):
            with open(histfile, "r", errors="ignore") as f:
                lines = f.readlines()
                return [l.split(';', 1)[1].strip() for l in lines if ';' in l]
        return []
    
    def obtener_todo_desde_fc(self):
        result = subprocess.run(['fc -l'], capture_output=True, text=True, shell=True)
        return result.stdout.splitlines() if result.stdout.strip() else []
    
