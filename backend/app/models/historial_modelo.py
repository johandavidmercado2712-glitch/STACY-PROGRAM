import os
import sys
import subprocess

class HistorialModelo: # muestra el historial de comandos del usuario dependiendo de su sistema operativo y tienen limite de 11 comandos 
    def obtener_desde_archivo(self):
        histfile = os.path.expanduser("~/.zsh_history") #define la ruta de windows "/home/juan/.zsh_history"
        if os.path.exists(histfile): #si exite continua sino retorna una lista vacia
            with open(histfile, "r", errors="ignore") as f:#abre el archivo en modo lectura y omite los errores de codificación
                lines = f.readlines() #lee todas las líneas del archivo y las almacena en una lista
                return [l.split(';', 1)[1].strip() for l in lines[-11:] if ';' in l] #retorna una lista con 11 comandos más recientes, eliminando la parte de tiempo y el número de comando
        return []

    def obtener_desde_fc(self):
        result = subprocess.run(['fc -l -11'], capture_output=True, text=True, shell=True)
        return result.stdout.splitlines() if result.stdout.strip() else []

    def obtener_desde_pipe(self):
        if not sys.stdin.isatty():
            data = sys.stdin.read()
            return data.splitlines()[-11:] if data.strip() else []
        return []
    
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
    
    def obtener_todo_desde_pipe(self):
        if not sys.stdin.isatty():
            data = sys.stdin.read()
            return data.splitlines() if data.strip() else []
        return []