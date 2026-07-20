"""
Endpoint POST /auth/google/exchange para la extensión VS Code.

Flujo:
1. La extensión inicia un servidor local y abre el navegador con la URL de Google
2. Google redirige al servidor local con un código de autorización
3. La extensión envía el código a este endpoint
4. Este endpoint canjea el código por tokens con Google
5. Obtiene la información del usuario (email, nombre)
6. Crea el usuario en la BD si no existe
7. Genera un JWT de STACY
8. Devuelve { access_token, username, email }
"""

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
import httpx
from uuid import uuid4
from auth.auth import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    create_access_token,
)
from config.usuarioDB import obtener_usuario_por_username, guardar_usuario, crear_tabla_usuarios
from auth.hashing import hash_password

TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

router = APIRouter()


class GoogleExchangeRequest(BaseModel):
    code: str
    client_id: str
    code_verifier: str | None = None
    redirect_uri: str


class GoogleExchangeResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    email: str


@router.post("/auth/google/exchange", response_model=GoogleExchangeResponse)
def google_exchange(data: GoogleExchangeRequest, request: Request, response: Response):
    # 1. Canjear el código por tokens con Google
    token_data = {
        "code": data.code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": data.redirect_uri,
        "grant_type": "authorization_code",
    }
    if data.code_verifier:
        token_data["code_verifier"] = data.code_verifier

    with httpx.Client() as client:
        resp = client.post(TOKEN_URL, data=token_data)
        tokens = resp.json()

    if "error" in tokens:
        raise HTTPException(
            status_code=400,
            detail=tokens.get("error_description", "Error al autenticar con Google"),
        )

    # 2. Obtener información del usuario
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    with httpx.Client() as client:
        resp = client.get(USERINFO_URL, headers=headers)
        user_info = resp.json()

    google_email = user_info.get("email", "")
    if not google_email:
        raise HTTPException(status_code=400, detail="No se pudo obtener el email de Google")

    google_name = user_info.get("name", google_email.split("@")[0])

    # 3. Crear usuario si no existe
    user = obtener_usuario_por_username(google_email)
    if not user:
        crear_tabla_usuarios()
        password_placeholder = hash_password(str(uuid4()))
        guardar_usuario(google_email, "", google_email, password_placeholder)
        user = obtener_usuario_por_username(google_email)
        if not user:
            raise HTTPException(status_code=500, detail="Error al crear usuario")

    # 4. Generar JWT de STACY
    token = create_access_token({"sub": user["USU_USERNAME"]})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=(request.url.scheme == "https"),
        samesite="strict",
        path="/",
        max_age=3600,
    )

    return GoogleExchangeResponse(
        access_token=token,
        username=user["USU_USERNAME"],
        email=google_email,
    )
