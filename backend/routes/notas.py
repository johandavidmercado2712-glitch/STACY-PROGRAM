"""
Notas — contrato de STACY-EXTENSION:

    GET    /notas        -> {"notas": [...]}
    POST   /notas        {titulo, contenido} -> 201
    PUT    /notas/{id}   {titulo, contenido}
    DELETE /notas/{id}
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from config.database import conexion
from routes.auth import usuario_actual

bp = APIRouter(prefix="/notas", tags=["notas"], dependencies=[Depends(usuario_actual)])


def _nota(fila):
    fila = dict(fila)
    fila["fecha_creacion"] = fila["fecha_creacion"].isoformat()
    fila["fecha_actualizacion"] = fila["fecha_actualizacion"].isoformat()
    return fila


class Nota(BaseModel):
    titulo: str = Field(min_length=1, max_length=300)
    contenido: str = Field(default="", max_length=20000)


@bp.get("")
def listar(usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        db.execute(
            "SELECT id, titulo, contenido, fecha_creacion, fecha_actualizacion"
            " FROM notas WHERE id_usuario = %s ORDER BY fecha_creacion DESC, id DESC",
            (id_usuario,),
        )
        filas = db.fetchall()
    return {"notas": [_nota(f) for f in filas]}


@bp.post("", status_code=201)
def crear(datos: Nota, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        db.execute(
            "INSERT INTO notas (id_usuario, titulo, contenido) VALUES (%s, %s, %s)"
            " RETURNING id",
            (id_usuario, datos.titulo, datos.contenido),
        )
        nueva = db.fetchone()
    return {"ok": True, "nota": {"id": nueva["id"], "titulo": datos.titulo,
                                 "contenido": datos.contenido}}


@bp.put("/{id_nota}")
def editar(id_nota: int, datos: Nota, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        db.execute(
            "UPDATE notas SET titulo = %s, contenido = %s, fecha_actualizacion = now()"
            " WHERE id = %s AND id_usuario = %s",
            (datos.titulo, datos.contenido, id_nota, id_usuario),
        )
        if db.rowcount == 0:
            raise HTTPException(status_code=404, detail="La nota no existe")
    return {"ok": True}


@bp.delete("/{id_nota}")
def borrar(id_nota: int, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        db.execute("DELETE FROM notas WHERE id = %s AND id_usuario = %s", (id_nota, id_usuario))
        if db.rowcount == 0:
            raise HTTPException(status_code=404, detail="La nota no existe")
    return {"ok": True}
