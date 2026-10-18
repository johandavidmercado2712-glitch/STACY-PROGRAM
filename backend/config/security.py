"""
JWT + hashing de contraseñas (sin passlib: bcrypt directo, sin dependencias viejas).

    crear_token(usuario)  -> str JWT con exp de 7 días
    leer_token(token)     -> payload o None si es inválido/expirado
    hash_password / verificar_password -> bcrypt

La clave secreta viene del entorno (SECRET_KEY). En producción es
obligatoria; en local se usa una de desarrollo para poder probar.
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

ES_PRODUCCION = os.environ.get("APP_ENV", "").lower() == "production"
SECRET_KEY = os.environ.get("SECRET_KEY", "")

if ES_PRODUCCION and not SECRET_KEY:
    raise RuntimeError("Configura SECRET_KEY en el entorno de producción.")

CLAVE_DESARROLLO = "stacy-dev-secret-solo-local"
TOKEN_DIAS = 7


def crear_token(usuario: dict) -> str:
    payload = {
        "sub": str(usuario["id"]),
        "username": usuario["username"],
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_DIAS),
    }
    return jwt.encode(payload, SECRET_KEY or CLAVE_DESARROLLO, algorithm="HS256")


def leer_token(token: str):
    """Devuelve el payload si el token es válido, o None si expiró/firma falsa."""
    try:
        return jwt.decode(
            token, SECRET_KEY or CLAVE_DESARROLLO, algorithms=["HS256"]
        )
    except jwt.PyJWTError:
        return None


def hash_password(contrasena: str) -> str:
    return bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(contrasena: str, hash_guardado: str) -> bool:
    try:
        return bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("utf-8"))
    except (ValueError, TypeError):
        return False
