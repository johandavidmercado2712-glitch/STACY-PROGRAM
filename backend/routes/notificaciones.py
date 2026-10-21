"""
Notificaciones - contrato de STACY-EXTENSION:

    GET /notificaciones -> {"notificaciones": [...]}  
                        -> Solo notificaciones del usuario actual
    GET /notificaciones?scope=team -> {"notificaciones": [...]}  
                        -> Notificaciones compartidas (team scope)
    GET /notificaciones?scope=all -> {"notificaciones": [...]}  
                        -> TODAS las notificaciones de todos los usuarios

La extension espera objetos con: id, titulo, mensaje, fecha, tipo, de, url
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from config.database import conexion
from routes.auth import usuario_actual

bp = APIRouter(prefix="/notificaciones", tags=["notificaciones"], dependencies=[Depends(usuario_actual)])


class Notificacion(BaseModel):
    id: int
    titulo: str = Field(min_length=1, max_length=300)
    mensaje: str = Field(default="", max_length=2000)
    fecha: str = Field(default="", max_length=100)
    tipo: str = Field(default="info", max_length=50)  # share, info, system
    de: str = Field(default="", max_length=200)  # nombre de quienorigin
    url: str = Field(default="", max_length=500)  # URL a la que llevar


def _notificacion(fila):
    fila = dict(fila)
    fila["fecha"] = fila["fecha"].isoformat() if hasattr(fila["fecha"], "isoformat") else str(fila["fecha"])
    return fila


@bp.get("")
def listar(scope: str = Query(default="user", regex="^(user|team|all)$"), usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        if scope == "team":
            # Notificaciones compartidas por medio de carpetas shared
            db.execute(
                "SELECT n.id, n.titulo, n.mensaje, n.tipo, n.de, n.url, n.fecha_creacion AS fecha"
                " FROM notificaciones n"
                " JOIN carpetas c ON c.id_usuario = n.id_usuario"
                " WHERE c.visibility = 'shared'"
                " AND (c.id_usuario = %s OR c.id IN (SELECT id_carpeta FROM carpeta_miembros WHERE id_usuario = %s))"
                " AND n.id_usuario != %s"  # excluir notificaciones propias del usuario actual
                " ORDER BY n.fecha_creacion DESC, n.id DESC",
                (id_usuario, id_usuario, id_usuario),
            )
        elif scope == "all":
            # TODAS las notificaciones de todos los usuarios
            db.execute(
                "SELECT id, titulo, mensaje, tipo, de, url, fecha_creacion AS fecha"
                " FROM notificaciones"
                " ORDER BY fecha_creacion DESC, id DESC"
            )
        else:
            # Por defecto: solo notificaciones del usuario actual
            db.execute(
                "SELECT id, titulo, mensaje, tipo, de, url, fecha_creacion AS fecha"
                " FROM notificaciones WHERE id_usuario = %s"
                " ORDER BY fecha_creacion DESC, id DESC",
                (id_usuario,),
            )
        filas = db.fetchall()
    return {"notificaciones": [_notificacion(f) for f in filas]}


@bp.post("/", status_code=201)
def crear(datos: Notificacion, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        db.execute(
            "INSERT INTO notificaciones (id_usuario, titulo, mensaje, tipo, de, url) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id"
            (id_usuario, datos.titulo, datos.mensaje, datos.tipo, datos.de, datos.url),
        )
        nueva = db.fetchone()
    return {"ok": True, "nota": {"id": nueva["id"]}}


@bp.delete("/{id_nota}")
def borrar(id_nota: int, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        db.execute("DELETE FROM notificaciones WHERE id = %s AND id_usuario = %s", (id_nota, id_usuario))
        if db.rowcount == 0:
            raise HTTPException(status_code=404, detail="La notificación no existe")
    return {"ok": True}
