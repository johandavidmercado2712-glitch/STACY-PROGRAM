import os  # interactuar con el sistema operativo
import platform  # detectar el sistema operativo
import subprocess  # ejecutar Comando de la terminal en python
import psutil  # extraer informacion del procesos
from datetime import datetime  # para la hora


def detectar_sistema():
    return platform.system()  # detexta si es windows o linux


def detectar_shell_windows():
    try:
        parent = (
            psutil.Process(os.getppid()).name().lower()
        )  # obtiene el id del proceso padre (en que terminal se ejecuta python), saca el nombre y y lo convierte en minuscula

        if "powershell" in parent or "pwsh" in parent:
            return "powershell"

        if "cmd" in parent:
            return "cmd"

    except Exception:
        pass

    return None


def obtener_historial_powershell(limite=None):
    path = os.path.join(  # sirve para crear la rutas uniendodolas para la ruta definitiva  C:\Users\TuUsuario\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
        os.environ.get(
            "APPDATA", ""
        ),  # obtiene la ruta de tu carpeta C:\Users\TuUsuario\AppData\Roaming
        "Microsoft",
        "Windows",
        "PowerShell",
        "PSReadLine",
        "ConsoleHost_history.txt",
    )

    if not os.path.exists(path):
        return []  # si no existe trae una carpeta vacia

    try:
        with open(
            path, encoding="utf-8", errors="ignore"
        ) as f:  # para abrir el archivocon la ruta creada en path =
            lines = [
                x.strip() for x in f.readlines() if x.strip()
            ]  # sirve para leer el archivo y organizarlos sin espacios ,saltos de linea y lineas vacias
            return lines[-limite:] if limite else lines

    except Exception:
        return []  # arroja una lista vacia si no se llega a cumplir


def obtener_historial_cmd(limite=None):
    try:
        result = subprocess.run(  # ejecuta el comando en la terminal para que obtener  los comandos
            ["doskey", "/history"],  # son comandos en el cmd para extraer los comandos
            capture_output=True,  # captura la salida al momento que se ejecute
            text=True,  # que lo que extraiga sea text
            shell=True,  # para comandos internos del cmd
        )

        comandos = (
            result.stdout.splitlines()
        )  # pasa de "dir\ncd Desktop" a ["dir", "cd Desktop"]

        return (
            comandos[-limite:] if limite else comandos
        )  # si el limite es limite =11 entonces solo mostrara11 comandos

    except Exception:
        return []


def obtener_historial(limite=None):

    sistema = detectar_sistema()

    if sistema == "Windows":
        # Intentar PowerShell primero
        comandos = obtener_historial_powershell(limite)
        if comandos:
            return comandos

        # Si PowerShell no tiene nada, intentar CMD
        comandos = obtener_historial_cmd(limite)
        if comandos:
            return comandos

        return []

    else:

        for archivo in ["~/.zsh_history", "~/.bash_history"]:

            path = os.path.expanduser(
                archivo
            )  # convierte ~/.bash_history en /home/usuario/.bash_history

            if os.path.exists(path):

                with open(path, errors="ignore") as f:
                    lines = [x.strip() for x in f.readlines() if x.strip()]
                    # Si es zsh, limpiar prefijo ': <timestamp>:<duracion>;'
                    if path.endswith(".zsh_history"):
                        lines = [limpiar_comando_zsh(x) for x in lines]
                    return lines[-limite:] if limite else lines

    return []
def limpiar_comando_zsh(linea: str) -> str: #sirve para quitar en la base de datos el tiempo de respuesta
    if not linea:
        return linea
    if linea.startswith(": "):
        separador = linea.find(";")
        if separador != -1 and separador + 1 < len(linea):
            return linea[separador + 1 :].strip()
    return linea.strip()


def extraer_ruta_del_comando(comando: str) -> str:
    """Extrae la ruta del comando si es un cd."""
    if comando.lower().startswith(
        "cd "
    ):  # convierte el comando en minusculas yverifica si el comando empieza por cd  para verificar si tiene ruta
        ruta = comando[
            3:
        ].strip()  # se sacael comando y el del caracter 3 para adelante es  0=c 1=d 2=espacio 3=d   = cd destrock y strip elimina espacios
        if ruta:
            return ruta
    return os.getcwd()  # obtiene la carpeta actual 


def obtener_historial_con_metadata(limite=None):
    """Retorna historial con comando, fecha y ruta."""
    comandos = obtener_historial(limite)
    resultado = []

    for comando in comandos:
        if comando:
            resultado.append(
                {
                    "comando": comando,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ruta": extraer_ruta_del_comando(comando),
                }
            )

    return resultado


class HistorialModelo:
    """Obtiene el historial de comandos (últimos 11)."""

    def obtener_desde_fc(self):
        return obtener_historial_con_metadata(limite=11)

    def obtener_desde_archivo(self):
        return obtener_historial_con_metadata(limite=11)


class HistorialModeloCompleto:
    """Obtiene todo el historial de comandos."""

    def obtener_todo_desde_fc(self):
        return obtener_historial_con_metadata()

    def obtener_todo_desde_archivo(self):
        return obtener_historial_con_metadata()