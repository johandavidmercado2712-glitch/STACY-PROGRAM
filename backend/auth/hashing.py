import hashlib, os
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex() + ':' + hash_obj.hex()

def verify_password(password: str, stored: str) -> bool:
    salt_hex, hash_hex = stored.split(':')
    salt = bytes.fromhex(salt_hex)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return hash_obj.hex() == hash_hex
