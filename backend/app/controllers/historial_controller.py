from app.models.historial_modelo import HistorialModelo
from app.views.historial_view import HistorialVista

class HistorialControlador:
    def __init__(self):
        self.modelo = HistorialModelo()
        self.vista = HistorialVista()

    def ejecutar(self):
        # Lógica de decisión: Prioridad Pipe > FC > Archivo
        comandos = self.modelo.obtener_desde_pipe()
        if comandos:
            self.vista.mostrar_comandos(comandos, "Comandos desde PIPE")
            return

        comandos = self.modelo.obtener_desde_fc()
        if comandos:
            self.vista.mostrar_comandos(comandos, "Comandos desde FC")
        else:
            comandos = self.modelo.obtener_desde_archivo()
            self.vista.mostrar_comandos(comandos, "Comandos desde ARCHIVO .zsh_history")
