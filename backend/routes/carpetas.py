"""
Carpetas — contrato de STACY-EXTENSION:

    GET    /carpetas                 -> {"carpetas": [...]}
    POST   /carpetas                 {nombre, descripcion} -> 201
    DELETE /carpetas/{id}
    POST   /carpetas/asignar         {com_id, car_id}
    POST   /carpetas/desasignar      {com_id, car_id}
    PUT    /carpetas/descripcion     {car_id, com_id, descripcion}
    GET    /carpetas/{id}/comandos   -> {"comandos": [...]}

La descripcion vive en la ASIGNACIÓN (carpeta_comando.descripcion),
porque la UI aplica descripciones a comandos dentro de una carpeta
(updateCommandDescription manda car_id + com_id + descripcion).
La UI lee CAR_ID o id; respondemos id (el parseData lo tolera).
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from config.database import conexion
from routes.auth import usuario_actual

bp = APIRouter(prefix="/carpetas", tags=["carpetas"], dependencies=[Depends(usuario_actual)])


def _carpeta(fila):
    fila = dict(fila)
    fila["fecha_creacion"] = fila["fecha_creacion"].isoformat()
    # Alias como los nombres que la extensión era capaz de leer antes.
    fila["CAR_ID"] = fila["id"]
    return fila


class CarpetaNueva(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)
    descripcion: str = Field(default="", max_length=2000)
    visibility: str = Field(default="private", max_length=20)
    team_id: int | None = None


class Asignacion(BaseModel):
    com_id: int
    car_id: int


class Descripcion(BaseModel):
    car_id: int
    com_id: int
    descripcion: str = Field(default="", max_length=2000)


def _cta_ids(usuario, com_id: int, car_id: int):
    """Valida que el comando y la carpeta pertenezcan al usuario y existan."""
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        db.execute("SELECT 1 FROM comandos WHERE id = %s AND id_usuario = %s", (com_id, id_usuario))
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="El comando no existe")
        db.execute("SELECT 1 FROM carpetas WHERE id = %s AND id_usuario = %s", (car_id, id_usuario))
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="La carpeta no existe")
    return id_usuario


from fastapi import Query

@bp.get("")
def listar(scope: str = Query(default="me"), usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        if scope == "team":
            db.execute(
                "SELECT id, nombre, descripcion, visibility, team_id, fecha_creacion FROM carpetas"
                " WHERE visibility='shared' AND (id_usuario=%s OR id IN (SELECT id_carpeta FROM carpeta_miembros WHERE id_usuario=%s))"
                " ORDER BY fecha_creacion DESC, id DESC",
                (id_usuario, id_usuario),
            )
        else:
            db.execute(
                "SELECT id, nombre, descripcion, visibility, team_id, fecha_creacion FROM carpetas"
                " WHERE id_usuario = %s ORDER BY fecha_creacion DESC, id DESC",
                (id_usuario,),
            )
        filas = db.fetchall()
    return {"carpetas": [_carpeta(f) for f in filas]}


@bp.post("", status_code=201)
def crear(datos: CarpetaNueva, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        db.execute(
            "SELECT id FROM carpetas WHERE id_usuario = %s AND nombre = %s",
            (id_usuario, datos.nombre),
        )
        if db.fetchone():
            raise HTTPException(status_code=409, detail="Ya tienes una carpeta con ese nombre")
        db.execute(
            "INSERT INTO carpetas (id_usuario, nombre, descripcion, visibility, team_id)"
            " VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (id_usuario, datos.nombre, datos.descripcion, datos.visibility, datos.team_id),
        )
        nueva = db.fetchone()
    return {"ok": True, "carpeta": {"id": nueva["id"], "CAR_ID": nueva["id"],
                                    "nombre": datos.nombre, "descripcion": datos.descripcion}}


@bp.delete("/{id_carpeta}")
def borrar(id_carpeta: int, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        db.execute("DELETE FROM carpetas WHERE id = %s AND id_usuario = %s", (id_carpeta, id_usuario))
        if db.rowcount == 0:
            raise HTTPException(status_code=404, detail="La carpeta no existe")
    return {"ok": True}


@bp.post("/asignar")
def asignar(datos: Asignacion, usuario=Depends(usuario_actual)):
    _cta_ids(usuario, datos.com_id, datos.car_id)
    with conexion() as db:
        db.execute(
            "INSERT INTO carpeta_comando (id_carpeta, id_comando) VALUES (%s, %s)"
            " ON CONFLICT DO NOTHING",
            (datos.car_id, datos.com_id),
        )
    return {"ok": True}


@bp.post("/desasignar")
def desasignar(datos: Asignacion, usuario=Depends(usuario_actual)):
    _cta_ids(usuario, datos.com_id, datos.car_id)
    with conexion() as db:
        db.execute("DELETE FROM carpeta_comando WHERE id_carpeta = %s AND id_comando = %s",
                   (datos.car_id, datos.com_id))
    return {"ok": True}


@bp.put("/descripcion")
def editar_descripcion(datos: Descripcion, usuario=Depends(usuario_actual)):
    _cta_ids(usuario, datos.com_id, datos.car_id)
    with conexion() as db:
        db.execute(
            "UPDATE carpeta_comando SET descripcion = %s"
            " WHERE id_carpeta = %s AND id_comando = %s",
            (datos.descripcion, datos.car_id, datos.com_id),
        )
        if db.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail="El comando no está asignado a esa carpeta")
    return {"ok": True}


@bp.get("/{id_carpeta}/comandos")
def por_carpeta(id_carpeta: int, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        db.execute("SELECT 1 FROM carpetas WHERE id = %s AND id_usuario = %s",
                   (id_carpeta, id_usuario))
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="La carpeta no existe")
        db.execute(
            """
            SELECT c.id, c.comando, c.directorio, c.fecha_ejecucion,
                   cc.descripcion
            FROM carpeta_comando cc
            JOIN comandos c ON c.id = cc.id_comando
            WHERE cc.id_carpeta = %s
            ORDER BY c.fecha_ejecucion DESC, c.id DESC
            """,
            (id_carpeta,),
        )
        filas = db.fetchall()
    comandos = []
    for f in filas:
        f = dict(f)
        f["fecha_ejecucion"] = f["fecha_ejecucion"].isoformat()
        comandos.append(f)
    return {"comandos": comandos}

class Miembro(BaseModel):
    user_id: int
    rol: str = Field(default="viewer", max_length=20)


@bp.post("/{id_carpeta}/miembros", status_code=201)
def agregar_miembro(id_carpeta: int, datos: Miembro, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        db.execute("SELECT 1 FROM carpetas WHERE id = %s AND id_usuario = %s", (id_carpeta, id_usuario))
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="La carpeta no existe")
        db.execute(
            "INSERT INTO carpeta_miembros (id_carpeta, id_usuario, rol) VALUES (%s, %s, %s)"
            " ON CONFLICT (id_carpeta, id_usuario) DO UPDATE SET rol = EXCLUDED.rol",
            (id_carpeta, datos.user_id, datos.rol),
        )
    return {"ok": True}


@bp.delete("/{id_carpeta}/miembros/{user_id}")
def quitar_miembro(id_carpeta: int, user_id: int, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        db.execute("SELECT 1 FROM carpetas WHERE id = %s AND id_usuario = %s", (id_carpeta, id_usuario))
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="La carpeta no existe")
        db.execute("DELETE FROM carpeta_miembros WHERE id_carpeta = %s AND id_usuario = %s", (id_carpeta, user_id))
    return {"ok": True}
