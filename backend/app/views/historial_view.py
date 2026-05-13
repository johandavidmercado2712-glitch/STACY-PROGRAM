class HistorialVista:
    def mostrar_comandos(self, comandos, titulo):
        print(f"\n--- {titulo} ---")
        if not comandos:
            print("No se encontraron comandos.")
        else:
            for comando in comandos:
                print(f"> {comando.strip()}")

class HistorialVistaCompleto:
    def mostrar_comandos_completos(self, comandos, titulo):
        print(f"\n--- {titulo} ---")
        if not comandos:
            print("No se encontraron comandos.")
        else:
            for comando in comandos:
                print(f"> {comando.strip()}")