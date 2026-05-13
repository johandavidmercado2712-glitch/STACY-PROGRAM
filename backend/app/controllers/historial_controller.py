from app.models.historial_modelo import HistorialModelo, HistorialModeloCompleto
from app.views.historial_view import HistorialVista, HistorialVistaCompleto

class HistorialControlador:
    def __init__(self):
        self.modelo = HistorialModelo()
        self.vista = HistorialVista()

    def ejecutar(self):
        # Lógica de decisión: Prioridad Pipe > FC > Archivo
        comandos = self.modelo.obtener_desde_pipe()
        if comandos:
            comandos =list(dict.fromkeys(comandos))# comando para eliminar comandos duplicados 
            self.vista.mostrar_comandos(comandos, "Comandos desde PIPE") #(stdin) - prioridad máxima
            return

        comandos = self.modelo.obtener_desde_fc()
        if comandos:
            comandos =list(dict.fromkeys(comandos))# comando para eliminar comandos duplicados
            self.vista.mostrar_comandos(comandos, "Comandos desde FC") #(comando fc -l -11)
        else:
            comandos =list(dict.fromkeys(comandos))# comando para eliminar comandos duplicados
            comandos = self.modelo.obtener_desde_archivo()
            self.vista.mostrar_comandos(comandos, "Comandos desde ARCHIVO .zsh_history")#(~/.zsh_history)


class HistorialControladorCompleto:
    def __init__(self):
        self.modelo = HistorialModeloCompleto()
        self.vista = HistorialVistaCompleto()

    def ejecutar(self):
        # Lógica de decisión: Prioridad Pipe > FC > Archivo
        comandos = self.modelo.obtener_todo_desde_pipe()
        if comandos:
            comandos =list(dict.fromkeys(comandos))# comando para eliminar comandos duplicados
            self.vista.mostrar_comandos_completos(comandos, "Todo el historial desde PIPE") #(stdin) - prioridad máxima
            return

        comandos = self.modelo.obtener_todo_desde_fc()
        if comandos:
            comandos =list(dict.fromkeys(comandos))# comando para eliminar comandos duplicados
            self.vista.mostrar_comandos_completos(comandos, "Todo el historial desde FC") #(comando fc -l)
        else:
            comandos = self.modelo.obtener_todo_desde_archivo()
            comandos =list(dict.fromkeys(comandos))# comando para eliminar comandos duplicados
            self.vista.mostrar_comandos_completos(comandos, "Todo el historial desde ARCHIVO .zsh_history")#(~/.zsh_history)