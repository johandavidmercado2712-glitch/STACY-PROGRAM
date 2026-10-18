"""
Historial de comandos — contrato de STACY-EXTENSION:

    GET  /historial/ultimos          últimos comandos (limit, default 50)
    GET  /historial/todos            todo el historial
    GET  /historial/comandos/{q}     búsqueda por texto
    POST /comandos/importar          lotes de 100: {comandos: [{comando, directorio}]}

Todas las lecturas responden {"comandos": [...]}: el parseData() de la
extensión acepta esa forma (también acepta 'data'/'datos'). Cada comando
expone comando, directorio y fecha_ejecucion, los claves que la UI lee.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from config.database import conexion
from routes.auth import usuario_actual

# Sin prefijo: las rutas llevan el path completo, así /comandos/importar
# no queda atrapada bajo /historial.
bp = APIRouter(
    tags=["historial"],
    dependencies=[Depends(usuario_actual)],
)


def _fila(fila):
    fila = dict(fila)
    fila["fecha_ejecucion"] = fila["fecha_ejecucion"].isoformat()
    return fila


@bp.get("/historial/ultimos")
def ultimos(limit: int = 50):
    limit = max(1, min(limit, 500))
    with conexion() as db:
        db.execute(
            "SELECT id, comando, directorio, fecha_ejecucion FROM comandos"
            " ORDER BY fecha_ejecucion DESC, id DESC LIMIT %s",
            (limit,),
        )
        filas = db.fetchall()
    return {"comandos": [_fila(f) for f in filas]}


@bp.get("/historial/todos")
def todos():
    with conexion() as db:
        db.execute(
            "SELECT id, comando, directorio, fecha_ejecucion FROM comandos"
            " ORDER BY fecha_ejecucion DESC, id DESC LIMIT 10000",
        )
        filas = db.fetchall()
    return {"comandos": [_fila(f) for f in filas]}


@bp.get("/historial/comandos/{consulta}")
def buscar(consulta: str):
    with conexion() as db:
        db.execute(
            "SELECT id, comando, directorio, fecha_ejecucion FROM comandos"
            " WHERE comando ILIKE %s"
            " ORDER BY fecha_ejecucion DESC, id DESC LIMIT 200",
            (f"%{consulta}%",),
        )
        filas = db.fetchall()
    return {"comandos": [_fila(f) for f in filas]}


class Importacion(BaseModel):
    comandos: list[dict] = Field(min_length=1, max_length=1000)


@bp.post("/comandos/importar")
def importar(exportacion: Importacion, usuario=Depends(usuario_actual)):
    """Subida por lotes (100) usada por los scripts generados. Es tolerante:
    ignora repeticiones dentro del lote y los comandos ya existentes con
    el mismo texto y directorio."""
    id_usuario = int(usuario["sub"])
    limpios, vistos = [], set()
    for item in exportacion.comandos:
        if not isinstance(item, dict):
            continue
        comando = str(item.get("comando", "")).strip()
        if not comando:
            continue
        directorio = str(item.get("directorio", "") or "")
        clave = (comando, directorio)
        if clave in vistos:
            continue
        vistos.add(clave)
        limpios.append(clave)
    if not limpios:
        raise HTTPException(status_code=400, detail="No hay comandos válidos en el lote")

    insertados = 0
    with conexion() as db:
        for comando, directorio in limpios:
            db.execute(
                "SELECT 1 FROM comandos WHERE id_usuario = %s AND comando = %s"
                " AND directorio = %s LIMIT 1",
                (id_usuario, comando, directorio),
            )
            if db.fetchone():
                continue
            db.execute(
                "INSERT INTO comandos (id_usuario, comando, directorio, fecha_ejecucion)"
                " VALUES (%s, %s, %s, %s) RETURNING id",
                (id_usuario, comando, directorio, datetime.now(timezone.utc)),
            )
            insertados += 1
    return {"ok": True, "recibidos": len(limpios), "insertados": insertados}
