import os
import sys
import subprocess

class HistorialModelo:
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

    def obtener_desde_pipe(self):
        if not sys.stdin.isatty():
            data = sys.stdin.read()
            return data.splitlines()[-11:] if data.strip() else []
        return []
