class HistorialVista:
    def mostrar_comandos(self, comandos, titulo):
        print(f"\n--- {titulo} ---")
        if not comandos:
            print("No se encontraron comandos.")
        else:
            for cmd_info in comandos:
                if isinstance(cmd_info, dict):
                    print(f"[{cmd_info['fecha']}] {cmd_info['ruta']}")
                    print(f"  > {cmd_info['comando']}")
                else:
                    print(f"> {cmd_info.strip()}")

class HistorialVistaCompleto:
    def mostrar_comandos_completos(self, comandos, titulo):
        print(f"\n--- {titulo} ---")
        if not comandos:
            print("No se encontraron comandos.")
        else:
            for cmd_info in comandos:
                if isinstance(cmd_info, dict):
                    print(f"[{cmd_info['fecha']}] {cmd_info['ruta']}")
                    print(f"  > {cmd_info['comando']}")
                else:
                    print(f"> {cmd_info.strip()}")