import subprocess

# Ejecutar el comando 'ls -l' (en Linux/macOS) o 'dir' (en Windows)
resultado = subprocess.run(['ls', '-l'], capture_output=True, text=True)

# Imprimir la salida del comando
print(resultado.stdout)
