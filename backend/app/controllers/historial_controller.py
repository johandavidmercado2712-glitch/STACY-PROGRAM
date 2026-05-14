from app.models.historial_modelo import HistorialModelo, HistorialModeloCompleto
from app.views.historial_view import HistorialVista, HistorialVistaCompleto

class HistorialControlador:
    def __init__(self):
        self.modelo = HistorialModelo()
        self.vista = HistorialVista()

    def ejecutar(self):
        comandos = self.modelo.obtener_desde_fc()
        if comandos:
            comandos = list(dict.fromkeys(comandos))  # Eliminar duplicados manteniendo el orden
            self.vista.mostrar_comandos(comandos, "Comandos desde FC") #(comando fc -l -11)
        else:
            comandos = self.modelo.obtener_desde_archivo()
            comandos = list(dict.fromkeys(comandos))  # Eliminar duplicados manteniendo el orden
            self.vista.mostrar_comandos(comandos, "Comandos desde ARCHIVO .zsh_history")#(~/.zsh_history)


class HistorialControladorCompleto:
    def __init__(self):
        self.modelo = HistorialModeloCompleto()
        self.vista = HistorialVistaCompleto()

    def ejecutar(self):

        comandos = self.modelo.obtener_todo_desde_fc()
        if comandos:
            comandos = list(dict.fromkeys(comandos))  # Eliminar duplicados manteniendo el orden
            self.vista.mostrar_comandos_completos(comandos, "Todo el historial desde FC") #(comando fc -l)
        else:
            comandos = self.modelo.obtener_todo_desde_archivo()
            comandos = list(dict.fromkeys(comandos))  # Eliminar duplicados manteniendo el orden
            self.vista.mostrar_comandos_completos(comandos, "Todo el historial desde ARCHIVO .zsh_history")#(~/.zsh_history)