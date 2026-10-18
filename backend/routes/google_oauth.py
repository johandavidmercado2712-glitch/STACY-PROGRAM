"""
Google OAuth — mismo flujo que hoy implementa la extensión:

    GET /auth/google/login?port=<puerto-local>
        -> redirige a Google para pedir consentimiento.
    GET /auth/google/callback?code=...&state=...
        -> cambia el code por id_token, crea/actualiza el usuario google,
           y redirige el navegador del usuario a:
               http://127.0.0.1:<port>/?token=<JWT-de-la-API>&user=<username>

El googleAuth.js de la extensión queda escuchando en 127.0.0.1:<port> y lee
`token` y `user` de esa query. (El paso 4 del plan mejorará esto enviando el
token por POST; hoy lo replicamos tal cual para no romper a los usuarios.)

Variables de entorno necesarias:
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
y en Google Cloud Console, redirect URI autorizado:
    https://<tu-dominio>/auth/google/callback

Sin esas variables, /auth/google/login responde 503 con explicación.
"""

import os
import secrets
import urllib.parse

import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from config.database import conexion
from config.security import crear_token

bp = APIRouter(tags=["auth"])

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")


def _scheme(host: str) -> str:
    # Local: http; detrás de Vercel u otro proxy HTTPS: https.
    return "http" if ("localhost" in host or "127.0.0.1" in host) else "https"


def _redirect_uri(host: str) -> str:
    return f"{_scheme(host)}://{host}/auth/google/callback"


def _separar_state(state: str):
    """state = '<nonce>.<port>' (lo generamos en /auth/google/login)."""
    if "." not in state:
        return None
    nonce, _, port = state.rpartition(".")
    if not nonce or not port.isdigit():
        return None
    return nonce, int(port)


@bp.get("/auth/google/login")
def google_login(port: int, request: Request):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Configura GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET en el entorno.",
        )
    host = request.headers.get("host", "")
    if not host:
        raise HTTPException(status_code=400, detail="No se recibió el host de la petición")
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": _redirect_uri(host),
        "response_type": "code",
        "scope": "openid email profile",
        # El puerto local viaja en el state, que Google devuelve integro en el callback.
        "state": f"{secrets.token_urlsafe(16)}.{port}",
        "prompt": "select_account",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return RedirectResponse(url, status_code=302)


@bp.get("/auth/google/callback")
def google_callback(code: str, state: str, request: Request):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Google OAuth no configurado.")

    separado = _separar_state(state)
    if not separado:
        raise HTTPException(status_code=400, detail="State inválido")
    _, puerto_local = separado

    host = request.headers.get("host", "")
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": _redirect_uri(host),
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
    if token_resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Google rechazó el código")

    id_token = token_resp.json().get("id_token", "")
    userinfo = requests.get(
        "https://oauth2.googleapis.com/tokeninfo",
        params={"id_token": id_token},
        timeout=15,
    )
    if userinfo.status_code != 200:
        raise HTTPException(status_code=401, detail="No se pudo validar la cuenta de Google")
    info = userinfo.json()
    if info.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Token de Google no corresponde a esta app")

    correo = info.get("email", "")
    if not correo:
        raise HTTPException(status_code=401, detail="Google no devolvió un correo")
    usuario_nombre_google = correo.split("@")[0] or "google_user"

    # Crea el usuario google (sin contraseña) o lo vincula si el correo ya existía.
    with conexion() as db:
        db.execute(
            "SELECT id, username FROM usuarios WHERE google_sub = %s",
            (info.get("sub"),),
        )
        usuario = db.fetchone()
        if not usuario:
            db.execute("SELECT id, username FROM usuarios WHERE correo = %s", (correo,))
            usuario = db.fetchone()
        if usuario:
            db.execute(
                "UPDATE usuarios SET google_sub = %s WHERE id = %s",
                (info.get("sub"), usuario["id"]),
            )
            final_id, final_username = usuario["id"], usuario["username"]
        else:
            db.execute(
                "INSERT INTO usuarios (username, apellidos, correo, provedor, google_sub)"
                " VALUES (%s, '', %s, 'google', %s) RETURNING id, username",
                (usuario_nombre_google, correo, info.get("sub")),
            )
            nuevo = db.fetchone()
            final_id, final_username = nuevo["id"], nuevo["username"]

    token = crear_token({"id": final_id, "username": final_username})

    destino = (
        f"http://127.0.0.1:{puerto_local}/"
        f"?token={urllib.parse.quote(token)}&user={urllib.parse.quote(final_username)}"
    )
    return RedirectResponse(destino, status_code=302)
