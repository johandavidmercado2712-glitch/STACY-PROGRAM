import os
import subprocess #ejecutar comandos de terminal desde python

def _detectar_historial():
    """Detecta el shell del usuario y devuelve la ruta del archivo de historial."""
    shell_env = os.environ.get('SHELL', '').lower()

    if 'zsh' in shell_env:
        histfile = os.path.expanduser("~/.zsh_history")
        if os.path.exists(histfile):
            return 'zsh', histfile

    if 'bash' in shell_env:
        histfile = os.path.expanduser("~/.bash_history")
        if os.path.exists(histfile):
            return 'bash', histfile

    # Fallback: verificar qué archivos existen
    zsh_hist = os.path.expanduser("~/.zsh_history")
    bash_hist = os.path.expanduser("~/.bash_history")

    if os.path.exists(zsh_hist):
        return 'zsh', zsh_hist
    if os.path.exists(bash_hist):
        return 'bash', bash_hist

    return None, None


def _parsear_comandos(lines, shell_type):
    """Parsea las líneas del historial según el formato del shell."""
    comandos = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if shell_type == 'zsh':
            # Formato zsh: :timestamp:duration;comando
            if ';' in line:
                comandos.append(line.split(';', 1)[1].strip())
        elif shell_type == 'bash':
            # Formato bash: cada línea es directamente el comando
            # (puede tener #timestamp en algunas configs, pero normalmente no)
            if not line.startswith('#'):
                comandos.append(line)
    return comandos


class HistorialModelo: # muestra el historial de comandos del usuario dependiendo de su sistema operativo y tienen limite de 11 comandos
    def obtener_desde_archivo(self):
        shell_type, histfile = _detectar_historial()
        if histfile and os.path.exists(histfile):
            with open(histfile, "r", errors="ignore") as f:
                lines = f.readlines()
                return _parsear_comandos(lines[-11:], shell_type)
        return []

    def obtener_desde_fc(self):
        result = subprocess.run(['fc -l -11'], capture_output=True, text=True, shell=True)
        return result.stdout.splitlines() if result.stdout.strip() else []



class HistorialModeloCompleto: #Muestra todo el historial de comandos del usuario sin limites
    def obtener_todo_desde_archivo(self):
        shell_type, histfile = _detectar_historial()
        if histfile and os.path.exists(histfile):
            with open(histfile, "r", errors="ignore") as f:
                lines = f.readlines()
                return _parsear_comandos(lines, shell_type)
        return []

    def obtener_todo_desde_fc(self):
        result = subprocess.run(['fc -l'], capture_output=True, text=True, shell=True)
        return result.stdout.splitlines() if result.stdout.strip() else []
    
