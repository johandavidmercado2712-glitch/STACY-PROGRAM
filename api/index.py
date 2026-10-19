"""
Adaptador VERCEL: exposición serverless de la app FastAPI.

Vercel usa este archivo como único entrypoint Python (ver vercel.json).
El backend completo vive en backend/; solo lo agregamos al path.

Corresponde a la plataforma de Vercel para Python (runtime >= Python 3.10).
No necesita `app.run()` ni uvicorn: Vercel ejecuta el ASGI directo.
"""

import sys
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BACKEND = RAIZ / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from routes.web import app  # noqa: E402  (app FastAPI de backend/routes/web.py)
app = app
