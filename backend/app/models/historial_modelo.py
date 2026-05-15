import os
import subprocess
import platform
import psutil

def _detectar_sistema():
    return platform.system() #detecta que sistema operativo uso

def _detectar_shell_windows():
    """Detecta el shell por el nombre del proceso padre."""
    try:
        parent = psutil.Process(os.getppid()).name().lower()
        
        if 'powershell' in parent or 'pwsh' in parent:
            return 'powershell'
        elif 'cmd' in parent:
            return 'cmd'
        else:
            # Verificar grandparent por si hay segundo nivel
            try:
                grandparent = psutil.Process(psutil.Process(os.getppid()).ppid()).name().lower()
                if 'powershell' in grandparent or 'pwsh' in grandparent:
                    return 'powershell'
                elif 'cmd' in grandparent:
                    return 'cmd'
            except:
                pass
    except:
        pass
    
    return None

def _obtener_historial_powershell(limite=None):
    historial_path = os.path.join(
        os.environ.get('APPDATA', ''),
        'Microsoft', 'Windows', 'PowerShell', 'PSReadLine',
        'ConsoleHost_history.txt'
    )
    
    if os.path.exists(historial_path):
        try:
            with open(historial_path, 'r', encoding='utf-8', errors='ignore') as f:
                lineas = f.readlines()
                if limite:
                    lineas = lineas[-limite:]
                return [linea.strip() for linea in lineas if linea.strip()]
        except Exception:
            return []
    return []


def _obtener_historial_cmd(limite=None):
    try:
         
        result = subprocess.run(['doskey', '/history'], capture_output=True, text=True, shell=True)
        comandos = result.stdout.splitlines() if result.stdout.strip() else []
        if limite:
            comandos = comandos[-limite:]
        return comandos
    except Exception:
        return []

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


class HistorialModelo:
    """Obtiene el historial de comandos del usuario (límite de 11)."""
    
    def _obtener_windows(self, limite=11):
        """Método unificado para obtener historial en Windows."""
        shell = _detectar_shell_windows()
        
        if shell == 'powershell':
            return _obtener_historial_powershell(limite)
        elif shell == 'cmd':
            return _obtener_historial_cmd(limite)
        else:
            # Fallback: intentar PowerShell primero, luego CMD
            comandos = _obtener_historial_powershell(limite)
            if comandos:
                return comandos
            return _obtener_historial_cmd(limite)
    
    def obtener_desde_archivo(self):
        sistema = _detectar_sistema()
        
        if sistema == "Windows":
            return self._obtener_windows(limite=11)
        else:
            shell_type, histfile = _detectar_historial()
            if histfile and os.path.exists(histfile):
                with open(histfile, "r", errors="ignore") as f:
                    lines = f.readlines()
                    return _parsear_comandos(lines[-11:], shell_type)
            return []
    
    def obtener_desde_fc(self):
        sistema = _detectar_sistema()
        
        if sistema == "Windows":
            return self._obtener_windows(limite=11)
        else:
            result = subprocess.run(['fc', '-l', '-11'], capture_output=True, text=True, shell=True)
            return result.stdout.splitlines() if result.stdout.strip() else []



class HistorialModeloCompleto:
    """Obtiene todo el historial de comandos sin límites."""
    
    def _obtener_windows_completo(self):
        """Método unificado para obtener historial completo en Windows."""
        shell = _detectar_shell_windows()
        
        if shell == 'powershell':
            return _obtener_historial_powershell()
        elif shell == 'cmd':
            return _obtener_historial_cmd()
        else:
            comandos = _obtener_historial_powershell()
            if comandos:
                return comandos
            return _obtener_historial_cmd()
    
    def obtener_todo_desde_archivo(self):
        sistema = _detectar_sistema()
        
        if sistema == "Windows":
            return self._obtener_windows_completo()
        else:
            result = subprocess.run(['fc', '-l'], capture_output=True, text=True, shell=True)
            return result.stdout.splitlines() if result.stdout.strip() else []
    
    def obtener_todo_desde_fc(self):
        sistema = _detectar_sistema()
        
        if sistema == "Windows":
            return self._obtener_windows_completo()
        else:
            shell_type, histfile = _detectar_historial()
            if histfile and os.path.exists(histfile):
                with open(histfile, "r", errors="ignore") as f:
                    lines = f.readlines()
                    return _parsear_comandos(lines, shell_type)
            return []