import hashlib, os
def hash_password(password: str) -> str:
    salt = os.urandom(16) #genera 16 bytes aleatorios para unirlo en la contrasena de bash
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600000) #se usa el algorithmo matematico sha256 + convierte el texto a bytes + salt aleatoriamente + el numero de vueltas (600000, recomendado OWASP)
    return salt.hex() + ':' + hash_obj.hex() # como el salt y el hash son bytes binarios raros el .hex() lo convierte en texto legible (numero y letras de la A a la F)

def verify_password(password: str, stored: str) -> bool: #verifica la contrasena que dijista el usuario en el login con la que se hasheo
    salt_hex, hash_hex = stored.split(':') #coge el string que se guardo de la contrasena en la base de datos y se parte en dos parte por el :  salt_hex y hash_hex
    salt = bytes.fromhex(salt_hex) #lo revierte a como estaba originalmente  antes de el os.urandom
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600000) #le aplica esto a la contrasena que dijito el usuario en el login (600000 vueltas)
    return hash_obj.hex() == hash_hex #verifica si las 2 contrasenas son iguales . si es asi devuelve un True o sino un False
