"""
Rutas de autenticación — contrato EXACTO que consume STACY-EXTENSION:

    POST /token          body form-urlencoded (username, password) -> {"access_token"}
    POST /register       body JSON {username, apellidos, correo, password}
    GET  /users/profile  Bearer JWT -> datos de la cuenta (401 si expiró)
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from config.database import conexion
from config.security import crear_token, hash_password, leer_token, verificar_password

bp = APIRouter(tags=["auth"])

oauth2 = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)


def usuario_actual(token: str = Depends(oauth2)):
    """Dependencia: valida el Bearer JWT y devuelve el payload.
    401 exactamente como espera la extensión (auto-logout)."""
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    payload = leer_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    return payload


class Registro(BaseModel):
    username: str = Field(min_length=1)
    apellidos: str = ""
    correo: EmailStr
    password: str = Field(min_length=6)


@bp.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    """Login exactamente como lo manda StacyClient.login():
    Content-Type application/x-www-form-urlencoded (OAuth2PasswordRequestForm)."""
    with conexion() as db:
        db.execute(
            "SELECT id, username, correo, password_hash, provedor"
            " FROM usuarios WHERE username = %s",
            (form.username,),
        )
        usuario = db.fetchone()

    if not usuario or not usuario["password_hash"] or not verificar_password(
        form.password, usuario["password_hash"]
    ):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    token = crear_token(usuario)
    return {"access_token": token, "token_type": "bearer"}


@bp.post("/register", status_code=201)
def register(datos: Registro):
    with conexion() as db:
        db.execute("SELECT 1 FROM usuarios WHERE username = %s", (datos.username,))
        if db.fetchone():
            raise HTTPException(status_code=409, detail="Ese username ya existe")
        db.execute("SELECT 1 FROM usuarios WHERE correo = %s", (datos.correo,))
        if db.fetchone():
            raise HTTPException(status_code=409, detail="Ese correo ya está registrado")
        db.execute(
            "INSERT INTO usuarios (username, apellidos, correo, password_hash, provedor)"
            " VALUES (%s, %s, %s, %s, 'local') RETURNING id, username, correo, provedor",
            (datos.username, datos.apellidos, datos.correo, hash_password(datos.password)),
        )
        usuario = db.fetchone()
    return {"ok": True, "usuario": dict(usuario)}


@bp.get("/users/profile")
def perfil(usuario=Depends(usuario_actual)):
    """La extensión lo usa cada refreshAll(): 401 -> logout automático."""
    with conexion() as db:
        db.execute(
            "SELECT id, username, apellidos, correo, provedor, fecha_creacion"
            " FROM usuarios WHERE id = %s",
            (int(usuario["sub"]),),
        )
        fila = db.fetchone()
    if not fila:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    fila = dict(fila)
    fila["fecha_creacion"] = fila["fecha_creacion"].isoformat()
    return fila
