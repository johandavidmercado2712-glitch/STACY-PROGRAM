from datetime import datetime, timedelta #enfocado en la hora y usarlo para calcular  la expiracion del token 
from typing_extensions import Annotated #para anotar  el tip de parametros de funciones como Depends
from urllib.parse import urlencode#conviete un un diccionario en un para metro de URL ejemplo {"a":1} == "a=1"
import jwt #crear y verificar token 
import os # ver y interactuar con los valores que estan en la variable de entorno .env
import httpx #para hacer peticiones a google. en pocas palabras un request
import time #para expirar los codigos de intercambio
from uuid import uuid4 # para generar id unicos aleatorios 
from dotenv import load_dotenv #para cargar y leer las vriables de entorno 
from fastapi import APIRouter, Depends, HTTPException, Cookie
from fastapi.responses import RedirectResponse #para el flujo de google y redirigir a los usuarios a otra url 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field # para validar y estructurar los datos 
from config.usuarioDB import obtener_usuario_por_username, guardar_usuario, crear_tabla_usuarios
from auth.hashing import hash_password, verify_password

load_dotenv()

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY == "STACY":
    raise RuntimeError(
        "SECRET_KEY no está configurada o es demasiado débil. "
        "Genera una con: openssl rand -hex 32"
    )
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5500")
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth" #la vista donde esta el login de google
TOKEN_URL = "https://oauth2.googleapis.com/token" #donde el servidor cangea el codigo
USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo" #donde obtienes el email y el nombre del usuario 


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")#define como extraer cada peticion

# Almacén temporal para códigos de intercambio OAuth (en producción usar Redis)
_exchange_codes: dict[str, dict] = {}

# Puerto del server local de la extensión (VS Code), asociado al state de la auth.
_oauth_ports: dict[str, dict] = {}


def create_access_token(payload: dict) -> str: #hace una copia del token . le anade la fecha y la firma 
    data = payload.copy() #se hace una copia no se afecta al original
    data["exp"] = datetime.utcnow() + timedelta(hours=1) #se anade la fecha
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM) # crea el token con esos 3 datos y la firma que es privada


def decode_token(token: str) -> dict: #verific y dcodifica un token si expiro o es invaido, lanza un error
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) 
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:#Extrae el token del header y devuelve los datos del usuario. 
    return decode_token(token)


class RegisterRequest(BaseModel):# define la  estructura del body esperado en /register. pydantic valida automaicamente los tipos 
    username: str
    apellidos: str
    correo: str
    password: str


@router.post("/register") #verifica que exitse el usuario , crea la tabla si no existe , hashea la contrasena , guarda el usuario en la base de datos 
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


@router.post("/token")#busca el usuario en la BD , verifica la contrasena con el hash, verifica que el usuario este activo, genera y devueve el JTW
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


@router.get("/auth/google/login") #Contruye la URL de google con los parametros necesarios y redirige al para que inicie session alli
def google_login(port: int | None = None, state: str | None = None):
    # Si la extension pasa `state` lo usa (anti-CSRF); sino lo genera.
    if not state:
        state = str(uuid4())
    # La extension pasa `port`: guardamos a que server local reenviar el code tras el callback.
    # Google SIEMPRE redirige a la URL https registrada (GOOGLE_REDIRECT_URI); el loopback
    # local (127.0.0.1) nunca se envia a Google, por eso no hay que registrarlo en Google Console.
    if port:
        _oauth_ports[state] = {"port": port, "exp": time.time() + 300}
    params = {
        "client_id": GOOGLE_CLIENT_ID, #el id con el cual google te reconoce
        "redirect_uri": GOOGLE_REDIRECT_URI, #url https registrada en Google Console
        "response_type": "code", #pide un codigo temporal de autorizacion 
        "scope": "openid email profile", #la informacion que le pides al usuario 
        "access_type": "online", #no necesitas acceso offline (sin refresh tokens)
        "state": state,
    }
    url = f"{AUTHORIZATION_URL}?{urlencode(params)}"
    response = RedirectResponse(url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        max_age=300, # 5 minutos
        samesite="lax",
    )
    return response


@router.get("/auth/google/callback")
def google_callback(
    code: str,
    state: str | None = None,
    oauth_state: Annotated[str | None, Cookie()] = None,
):#Google llama a esta URL automáticamente con un code temporal en la query string
    if not oauth_state or not state or oauth_state != state:
        raise HTTPException(
            status_code=400,
            detail="Validación de estado (CSRF) fallida o expirada."
        )
    # Recuperar el puerto de la extension (si venia del flujo de VS Code).
    entry = _oauth_ports.pop(state, None)
    exchange_code = _generar_codigo_intercambio(code)
    if entry and entry.get("port"):
        # Reenviar el code de intercambio al server local de la extension (loopback, sin Google).
        redirect_url = f"http://127.0.0.1:{entry['port']}?code={exchange_code}&state={state}"
    else:
        # Flujo web: el frontend canjea el code.
        redirect_url = f"{FRONTEND_URL}?code={exchange_code}"
    response = RedirectResponse(redirect_url)
    response.delete_cookie("oauth_state")
    return response


def _generar_codigo_intercambio(google_code: str) -> str:
    """Canjea el code de Google por un JWT y lo almacena tras un código de un solo uso."""
    with httpx.Client() as client:
        resp = client.post(TOKEN_URL, data={
            "code": google_code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        tokens = resp.json()

    if "error" in tokens:
        raise HTTPException(status_code=400, detail=tokens.get("error_description", "Error al autenticar con Google"))

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    with httpx.Client() as client:
        resp = client.get(USERINFO_URL, headers=headers)
        user_info = resp.json()

    google_email = user_info["email"]
    google_name = user_info.get("name", google_email.split("@")[0])

    user = obtener_usuario_por_username(google_email)
    if not user:
        crear_tabla_usuarios()
        password_placeholder = hash_password(str(uuid4()))
        guardar_usuario(google_email, "", google_email, password_placeholder)
        user = obtener_usuario_por_username(google_email)

    token = create_access_token({"sub": user["USU_USERNAME"]})
    exchange_code = str(uuid4())
    _exchange_codes[exchange_code] = {
        "token": token,
        "username": user["USU_USERNAME"],
        "exp": time.time() + 300,
    }
    return exchange_code


class ExchangeRequest(BaseModel):
    code: str


@router.post("/auth/exchange")
def intercambiar_codigo(data: ExchangeRequest):
    """Canjea un código de un solo uso por el JWT (evita leak en URL)."""
    entry = _exchange_codes.pop(data.code, None)
    if not entry:
        raise HTTPException(status_code=400, detail="Código inválido o expirado")
    if entry.get("exp") and time.time() > entry["exp"]:
        raise HTTPException(status_code=400, detail="Código inválido o expirado")
    return {
        "access_token": entry["token"],
        "token_type": "bearer",
        "username": entry["username"],
    }

