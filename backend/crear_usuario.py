from auth.hashing import hash_password
from config.usuarioDB import guardar_usuario, crear_tabla_usuarios
username = input("Username: ")
apellidos = input("Apellidos: ")
correo = input("Correo: ")
password = input("Password: ")
password_hash = hash_password(password)
crear_tabla_usuarios()
guardar_usuario(username, apellidos, correo, password_hash)
print("Usuario creado exitosamente")