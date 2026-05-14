import os
import sys
import subprocess
import platform

class HistorialModelo:                                # muestra el historial de comandos del usuario dependiendo de su sistema operativo y tienen limite de 11 comandos 
    
    def _es_comando_valido(self, linea):
    #Verifica si una línea es un comando válido de terminal"""
        indicadores_invalidos = [
        'text-align:',      # CSS
        'font-size:',       # CSS
        'background:',      # CSS
        'padding:',         # CSS
        'SELECT ',          # SQL (con espacio)
        'INSERT INTO',     # SQL
        '<html',            # HTML
        '<!DOCTYPE',        # HTML
        'conn =',           # Python
        'cursor.execute'    # Python
        ]
    
    
        
        for indicador in indicadores_invalidos:
            if indicador in linea:
                return False
        return True
    
    def obtener_desde_archivo(self):
        so = platform.system()
    
        archivos_candidatos = []
        
        if so != 'Windows':
            archivos_candidatos.append(os.path.expanduser("~/.zsh_history"))  # Cambiar orden: zsh primero
            archivos_candidatos.append(os.path.expanduser("~/.bash_history"))
        else:
            archivos_candidatos.append(os.path.expanduser("~/AppData/Roaming/Microsoft/Windows/PowerShell/PSReadline/ConsoleHost_history.txt"))
        
        mejores_comandos = []
        
        for histfile in archivos_candidatos:
            if os.path.exists(histfile):
                with open(histfile, "r", errors="ignore") as f:
                    lines = f.readlines()
                    comandos = [l.split(';', 1)[1].strip() for l in lines[-11:] if ';' in l and self._es_comando_valido(l)]
                    if len(comandos) > len(mejores_comandos):
                        mejores_comandos = comandos
        
        return mejores_comandos

    def obtener_desde_fc(self):                                                        #sirve para mostrar el historial de comandos del usuario utilizando el comando fc -l -11, que muestra los últimos 11 comandos ejecutados en la terminal

        so = platform.system()
        shell = os.environ.get('SHELL', '')
        
        if so == 'Windows':
            result = subprocess.run(['doskey /history'], capture_output=True, text=True, shell=True)
            return result.stdout.splitlines()[-11:] if result.stdout.strip() else []
        else:  # Linux/WSL
            if 'zsh' in shell:
                result = subprocess.run(['fc -l -11'], capture_output=True, text=True, shell=True)
                if result.stdout.strip():
                    return result.stdout.splitlines()
            # Fallback bash
            result = subprocess.run(['history -16'], capture_output=True, text=True, shell=True)
            return result.stdout.splitlines()[-11:] if result.stdout.strip() else []

    
class HistorialModeloCompleto:     #Muestra todo el historial de comandos del usuario sin limites 
    
    def _es_comando_valido(self, linea):
        #Verifica si una línea es un comando válido de terminal"""
        indicadores_invalidos = ['{', '}', 'SELECT', 'INSERT', '<html', '<!DOCTYPE', 
                                'font-size', 'background:', 'text-align', 'padding:', 
                                'conn =', 'cursor.execute']
        
        for indicador in indicadores_invalidos:
            if indicador in linea:
                return False
        return True
    
    def obtener_todo_desde_archivo(self):
        so = platform.system()
        
        archivos_candidatos = []
        
        if so != 'Windows':
            archivos_candidatos.append(os.path.expanduser("~/.bash_history"))
            archivos_candidatos.append(os.path.expanduser("~/.zsh_history"))
        else:
            archivos_candidatos.append(os.path.expanduser("~/AppData/Roaming/Microsoft/Windows/PowerShell/PSReadline/ConsoleHost_history.txt"))
        
        mejores_comandos = []
        
        for histfile in archivos_candidatos:
            if os.path.exists(histfile):
                with open(histfile, "r", errors="ignore") as f:
                    lines = f.readlines()
                    comandos = [l.split(';', 1)[1].strip() for l in lines if ';' in l and self._es_comando_valido(l)]
                    if len(comandos) > len(mejores_comandos):
                        mejores_comandos = comandos
        
        return mejores_comandos
        
    def obtener_todo_desde_fc(self):
        so = platform.system()
        shell = os.environ.get('SHELL', '')
        
        if so == 'Windows':
            result = subprocess.run(['doskey /history'], capture_output=True, text=True, shell=True)
            return result.stdout.splitlines() if result.stdout.strip() else []
        else:  # Linux/WSL
            if 'zsh' in shell:
                result = subprocess.run(['fc -l'], capture_output=True, text=True, shell=True)
                if result.stdout.strip():
                    return result.stdout.splitlines()
            # Fallback bash
            result = subprocess.run(['history -16'], capture_output=True, text=True, shell=True)
            return result.stdout.splitlines() if result.stdout.strip() else []
