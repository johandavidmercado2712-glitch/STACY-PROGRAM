from app.models.historial_modelo import HistorialModelo, HistorialModeloCompleto
from app.views.historial_view import HistorialVista, HistorialVistaCompleto
from config.db import guardar_comando


def eliminar_duplicados(comandos):
    """Elimina comandos duplicados manteniendo el orden."""
    vistos = set()
    resultado = []

    for cmd_info in comandos:
        if isinstance(cmd_info, dict):
            if cmd_info["comando"] not in vistos:
                vistos.add(cmd_info["comando"])
                resultado.append(cmd_info)
        else:
            if cmd_info not in vistos:
                vistos.add(cmd_info)
                resultado.append(cmd_info)
    return resultado


def guardar_en_bd(comandos):
    """Guarda todos los comandos en la BD."""
    for cmd_info in comandos:
        if isinstance(cmd_info, dict):
            guardar_comando(cmd_info["comando"], cmd_info["ruta"])


class HistorialControlador:

    def __init__(self):
        self.modelo = HistorialModelo()
        self.vista = HistorialVista()

    def ejecutar(self):
        comandos = self.modelo.obtener_desde_fc()
        if comandos:
            comandos = eliminar_duplicados(comandos)
            guardar_en_bd(comandos)
            self.vista.mostrar_comandos(comandos, "Comandos desde FC")
        else:
            comandos = self.modelo.obtener_desde_archivo()
            comandos = eliminar_duplicados(comandos)
            guardar_en_bd(comandos)
            self.vista.mostrar_comandos(comandos, "Comandos desde ARCHIVO")


class HistorialControladorCompleto:

    def __init__(self):
        self.modelo = HistorialModeloCompleto()
        self.vista = HistorialVistaCompleto()

    def ejecutar(self):
        comandos = self.modelo.obtener_todo_desde_fc()
        if comandos:
            comandos = eliminar_duplicados(comandos)
            guardar_en_bd(comandos)
            self.vista.mostrar_comandos_completos(
                comandos, "Todo el historial desde FC"
            )
        else:
            comandos = self.modelo.obtener_todo_desde_archivo()
            comandos = eliminar_duplicados(comandos)
            guardar_en_bd(comandos)
            self.vista.mostrar_comandos_completos(
                comandos, "Todo el historial desde ARCHIVO"
            )


class MostrarComandos:
    def __init__(self):
        self.modelo = HistorialModelo()
        self.vista = HistorialVista()

    def ejecutar(self):
        comandos = self.modelo.obtener_desde_fc()
        if comandos:
            comandos = eliminar_duplicados(comandos)
            guardar_en_bd(comandos)
            self.vista.mostrar_comandos(comandos, "Comandos desde FC")
            return comandos
        else:
            comandos = self.modelo.obtener_desde_archivo()
            comandos = eliminar_duplicados(comandos)
            guardar_en_bd(comandos)
            self.vista.mostrar_comandos(comandos, "Comandos desde ARCHIVO")
            return comandos


class MostrarComandosCompletos:
    def __init__(self):
        self.modelo = HistorialModeloCompleto()
        self.vista = HistorialVista()

    def ejecutar(self):
        comandos = self.modelo.obtener_todo_desde_fc()
        if comandos:
            comandos = eliminar_duplicados(comandos)
            guardar_en_bd(comandos)
            self.vista.mostrar_comandos(comandos, "Comando Desde Archivo")
            return comandos
        else:
            comandos = self.modelo.obtener_todo_desde_archivo()
            comandos = eliminar_duplicados(comandos)
            guardar_en_bd(comandos)
            self.vista.mostrar_comandos(comandos, "Comandos Desde Archivo")
            return comandos
