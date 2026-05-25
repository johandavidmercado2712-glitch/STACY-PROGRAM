from datetime import datetime, timedelta #timedelta es para sumar o restar
from typing_extensions import Annotated
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm #sabe como extraer el token del usuario ,  sabe como recibir el formulario de username y password

SECRET_KEY = "stacy"
ALGORITHM = "HS256"

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

users = {
    "jason": {"username": "pablo", "email": "pablo@red.com", "password": "string"}
}


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


@router.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = users.get(form_data.username)

    if not user or form_data.password != user["password"]:
        raise HTTPException(status_code=400, detail="Usuario o contrasena incorrecta")

    token = create_access_token({"username": user["username"], "email": user["email"]})
    return {"access_token": token, "token_type": "bearer"}
