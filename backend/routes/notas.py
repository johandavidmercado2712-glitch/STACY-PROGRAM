"""
Notas — contrato de STACY-EXTENSION:

    GET    /notas               -> {"notas": [...]}
    GET    /notas?scope=shared  -> {"notas": [...]} (notas compartidas)
    POST   /notas               {titulo, contenido} -> 201
    PUT    /notas/{id}          {titulo, contenido}
    DELETE /notas/{id}
    PUT    /notas/{id}/visibilidad  {visibility}
    POST   /notas/{id}/miembros {user_id, rol} -> 201
    DELETE /notas/{id}/miembros/{user_id}
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
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


class NotaConVisibilidad(BaseModel):
    titulo: str = Field(min_length=1, max_length=300)
    contenido: str = Field(default="", max_length=20000)
    visibility: str = Field(default="private", max_length=20)


class Visibilidad(BaseModel):
    visibility: str = Field(default="private", max_length=20)


class Miembro(BaseModel):
    user_id: int
    rol: str = Field(default="viewer", max_length=20)


@bp.get("")
def listar(scope: str = Query(default="me", regex="^(me|shared|all)$"), usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        if scope == "shared":
            # Notas compartidas: propias con visibility='shared' + notas donde soy miembro
            db.execute(
                "SELECT DISTINCT n.id, n.titulo, n.contenido, n.visibility, n.fecha_creacion, n.fecha_actualizacion"
                " FROM notas n"
                " WHERE (n.id_usuario = %s AND n.visibility = 'shared')"
                " OR n.id IN (SELECT id_nota FROM nota_miembros WHERE id_usuario = %s)"
                " ORDER BY n.fecha_creacion DESC, n.id DESC",
                (id_usuario, id_usuario),
            )
        elif scope == "all":
            # Todas las notas visibles para el usuario (propias + compartidas)
            db.execute(
                "SELECT DISTINCT n.id, n.titulo, n.contenido, n.visibility, n.fecha_creacion, n.fecha_actualizacion"
                " FROM notas n"
                " WHERE n.id_usuario = %s"
                " OR n.id IN (SELECT id_nota FROM nota_miembros WHERE id_usuario = %s)"
                " ORDER BY n.fecha_creacion DESC, n.id DESC",
                (id_usuario, id_usuario),
            )
        else:
            # Por defecto: solo notas propias
            db.execute(
                "SELECT id, titulo, contenido, visibility, fecha_creacion, fecha_actualizacion"
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
            "INSERT INTO notas (id_usuario, titulo, contenido, visibility) VALUES (%s, %s, %s, 'private')"
            " RETURNING id",
            (id_usuario, datos.titulo, datos.contenido),
        )
        nueva = db.fetchone()
    return {"ok": True, "nota": {"id": nueva["id"], "titulo": datos.titulo,
                                  "contenido": datos.contenido, "visibility": "private"}}


@bp.put("/{id_nota}")
def editar(id_nota: int, datos: Nota, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        # Verificar que el usuario sea propietario o tenga rol editor
        db.execute(
            "SELECT 1 FROM notas WHERE id = %s AND id_usuario = %s"
            " UNION"
            " SELECT 1 FROM nota_miembros WHERE id_nota = %s AND id_usuario = %s AND rol = 'editor'",
            (id_nota, id_usuario, id_nota, id_usuario),
        )
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="La nota no existe o no tienes permisos")
        db.execute(
            "UPDATE notas SET titulo = %s, contenido = %s, fecha_actualizacion = now()"
            " WHERE id = %s",
            (datos.titulo, datos.contenido, id_nota),
        )
        if db.rowcount == 0:
            raise HTTPException(status_code=404, detail="La nota no existe")
    return {"ok": True}


@bp.delete("/{id_nota}")
def borrar(id_nota: int, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        # Solo el propietario puede borrar
        db.execute("DELETE FROM notas WHERE id = %s AND id_usuario = %s", (id_nota, id_usuario))
        if db.rowcount == 0:
            raise HTTPException(status_code=404, detail="La nota no existe o no eres el propietario")
    return {"ok": True}


@bp.put("/{id_nota}/visibilidad")
def cambiar_visibilidad(id_nota: int, datos: Visibilidad, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    if datos.visibility not in ("private", "shared"):
        raise HTTPException(status_code=400, detail="visibility debe ser 'private' o 'shared'")
    with conexion() as db:
        # Solo el propietario puede cambiar la visibilidad
        db.execute("UPDATE notas SET visibility = %s WHERE id = %s AND id_usuario = %s",
                   (datos.visibility, id_nota, id_usuario))
        if db.rowcount == 0:
            raise HTTPException(status_code=404, detail="La nota no existe o no eres el propietario")
    return {"ok": True}


@bp.post("/{id_nota}/miembros", status_code=201)
def agregar_miembro(id_nota: int, datos: Miembro, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        # Verificar que el usuario sea propietario de la nota
        db.execute("SELECT 1 FROM notas WHERE id = %s AND id_usuario = %s", (id_nota, id_usuario))
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="La nota no existe o no eres el propietario")
        # Verificar que el usuario a agregar exista
        db.execute("SELECT id, username FROM usuarios WHERE id = %s", (datos.user_id,))
        usuario_destino = db.fetchone()
        if not usuario_destino:
            raise HTTPException(status_code=404, detail="El usuario no existe")
        # No permitir que el propietario se agregue a sí mismo
        if datos.user_id == id_usuario:
            raise HTTPException(status_code=400, detail="No puedes agregarte a tu propia nota")
        # Agregar miembro
        db.execute(
            "INSERT INTO nota_miembros (id_nota, id_usuario, rol) VALUES (%s, %s, %s)"
            " ON CONFLICT (id_nota, id_usuario) DO UPDATE SET rol = EXCLUDED.rol"
            " RETURNING id_nota",
            (id_nota, datos.user_id, datos.rol),
        )
        if not db.fetchone():
            raise HTTPException(status_code=409, detail="Ya existe la asignación")
        # Cambiar visibilidad a shared automáticamente
        db.execute("UPDATE notas SET visibility = 'shared' WHERE id = %s AND visibility = 'private'", (id_nota,))
        # Crear notificación para el usuario invitado
        db.execute(
            "SELECT titulo FROM notas WHERE id = %s",
            (id_nota,),
        )
        nota = db.fetchone()
        if nota:
            db.execute(
                "INSERT INTO notificaciones (id_usuario, titulo, mensaje, tipo, de)"
                " VALUES (%s, %s, %s, %s, %s)",
                (datos.user_id, f"Nota compartida: {nota['titulo']}",
                 f"Te han invitado a ver la nota '{nota['titulo']}'", "share", usuario["username"]),
            )
    return {"ok": True, "miembro": {"user_id": datos.user_id, "rol": datos.rol}}


@bp.delete("/{id_nota}/miembros/{user_id}")
def quitar_miembro(id_nota: int, user_id: int, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        # Verificar que el usuario sea propietario de la nota
        db.execute("SELECT 1 FROM notas WHERE id = %s AND id_usuario = %s", (id_nota, id_usuario))
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="La nota no existe o no eres el propietario")
        # Quitar miembro
        db.execute("DELETE FROM nota_miembros WHERE id_nota = %s AND id_usuario = %s", (id_nota, user_id))
        if db.rowcount == 0:
            raise HTTPException(status_code=404, detail="El usuario no es miembro de esta nota")
        # Si no quedan miembros, cambiar visibilidad a private
        db.execute("SELECT COUNT(*) as count FROM nota_miembros WHERE id_nota = %s", (id_nota,))
        resultado = db.fetchone()
        if resultado and resultado["count"] == 0:
            db.execute("UPDATE notas SET visibility = 'private' WHERE id = %s", (id_nota,))
    return {"ok": True}


@bp.get("/{id_nota}/miembros")
def listar_miembros(id_nota: int, usuario=Depends(usuario_actual)):
    id_usuario = int(usuario["sub"])
    with conexion() as db:
        # Verificar que el usuario sea propietario o miembro
        db.execute(
            "SELECT 1 FROM notas WHERE id = %s AND id_usuario = %s"
            " UNION"
            " SELECT 1 FROM nota_miembros WHERE id_nota = %s AND id_usuario = %s",
            (id_nota, id_usuario, id_nota, id_usuario),
        )
        if not db.fetchone():
            raise HTTPException(status_code=404, detail="No tienes acceso a esta nota")
        db.execute(
            "SELECT nm.id_usuario, nm.rol, u.username"
            " FROM nota_miembros nm"
            " JOIN usuarios u ON u.id = nm.id_usuario"
            " WHERE nm.id_nota = %s",
            (id_nota,),
        )
        miembros = db.fetchall()
    return {"miembros": [dict(m) for m in miembros]}
