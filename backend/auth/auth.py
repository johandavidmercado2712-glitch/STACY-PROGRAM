from datetime import datetime, timedelta
from typing_extensions import Annotated
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from config.usuarioDB import obtener_usuario_por_username, guardar_usuario, crear_tabla_usuarios
from auth.hashing import hash_password, verify_password
SECRET_KEY = "stacy"
ALGORITHM = "HS256"

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token") #sabe com extraer el token del header





def create_access_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    return decode_token(token)


class RegisterRequest(BaseModel):
    username: str
    apellidos: str
    correo: str
    password: str


@router.post("/register")
def register(data: RegisterRequest):
    user = obtener_usuario_por_username(data.username)
    if user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    crear_tabla_usuarios()
    password_hash = hash_password(data.password)
    ok = guardar_usuario(data.username, data.apellidos, data.correo, password_hash)
    if not ok:
        raise HTTPException(status_code=500, detail="Error al guardar usuario")
    return {"mensaje": "Usuario registrado exitosamente"}


@router.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = obtener_usuario_por_username(form_data.username)
    
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales Invalidas")
    if not verify_password(form_data.password, user["USU_PASSWORD_HASH"]):
        raise HTTPException(status_code=401, detail="Credenciales Invalidas")
    if user["USU_ACTIVO"] != 1:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    token = create_access_token({"sub": user["USU_USERNAME"]})
    return {"access_token": token, "token_type": "bearer"}
