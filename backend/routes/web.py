"""
NIVEL DE ENSAMBLE: arma la aplicación FastAPI de STACY.

Aquí se registran todos los routers y se define la raíz verificable:

    uvicorn routes.web:app   (desde backend/)
Después la extensión apunta a http://127.0.0.1:8000 con
vscode.workspace.getConfiguration('stacy').update('serverUrl', ...).

Rutas incluidas (contrato de STACY-EXTENSION):
    /token, /register, /users/profile
    /historial/ultimos, /historial/todos, /historial/comandos/{q}
    /comandos/importar
    /carpetas, /carpetas/{id}, /carpetas/asignar, /carpetas/desasignar,
    /carpetas/descripcion, /carpetas/{id}/comandos
    /notas, /notas/{id}
    /notificaciones, /notificaciones/{id}   ← NUEVO
    /auth/google/login, /auth/google/callback
    /api (raiz JSON, antes en /), /salud (health check)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.database import conexion
from routes import auth, carpetas, google_oauth, historial, notas, notificaciones

app = FastAPI(
    title="STACY API",
    description="Backend de STACY (historial de comandos, carpetas y notas).",
    version="1.0.0",
)

# CORS abierto: la extensión hace fetch desde el extension host (sin CORS),
# pero un futuro sitio web de STACY sí se beneficia. No exponemos cookies.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Routers del contrato
app.include_router(auth.bp)
app.include_router(historial.bp)
app.include_router(carpetas.bp)
app.include_router(notas.bp)
app.include_router(notificaciones.bp)  # ← NUEVO
app.include_router(google_oauth.bp)


@app.get("/api")
def raiz():
    return {"ok": True, "mensaje": "STACY API operativa.", "docs": "/docs"}


@app.get("/salud")
def salud():
    """Verificación simple de app + base de datos."""
    import logging
    logger = logging.getLogger("uvicorn.error")
    try:
        with conexion() as db:
            db.execute("SELECT 1")
            db.fetchone()
    except Exception as exc:
        logger.error("Fallo la conexión a la base de datos: %s", exc)
        return JSONResponse(status_code=500, content={"ok": False, "error": str(exc)})
    return {"ok": True, "mensaje": "STACY API + PostgreSQL responden"}
