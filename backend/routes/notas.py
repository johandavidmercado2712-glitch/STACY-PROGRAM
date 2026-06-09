from fastapi import APIRouter, Depends, HTTPException
from typing_extensions import Annotated
from pydantic import BaseModel

from auth.auth import get_current_user
from config.usuarioDB import obtener_usuario_por_username
from config.notasBD import (
    guardar_nota,
    obtener_notas,
    obtener_nota_por_id,
    actualizar_nota,
    eliminar_nota,
)

router = APIRouter()


class CrearNotaRequest(BaseModel):
    titulo: str
    contenido: str = ""


class ActualizarNotaRequest(BaseModel):
    titulo: str
    contenido: str = ""


def get_usu_id(my_user: dict) -> int:
    user = obtener_usuario_por_username(my_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user["USU_ID"]


@router.get("/notas")
def listar_notas(my_user: Annotated[dict, Depends(get_current_user)]):
    usu_id = get_usu_id(my_user)
    notas = obtener_notas(usu_id)
    return {"notas": notas}


@router.post("/notas")
def crear_nota(
    data: CrearNotaRequest,
    my_user: Annotated[dict, Depends(get_current_user)],
):
    usu_id = get_usu_id(my_user)
    not_id = guardar_nota(data.titulo, data.contenido, usu_id)
    if not_id is None:
        raise HTTPException(status_code=500, detail="Error al crear nota")
    return {"mensaje": "Nota creada", "not_id": not_id}


@router.get("/notas/{not_id}")
def obtener_nota(
    not_id: int,
    my_user: Annotated[dict, Depends(get_current_user)],
):
    usu_id = get_usu_id(my_user)
    nota = obtener_nota_por_id(not_id, usu_id)
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return nota


@router.put("/notas/{not_id}")
def actualizar_nota_endpoint(
    not_id: int,
    data: ActualizarNotaRequest,
    my_user: Annotated[dict, Depends(get_current_user)],
):
    usu_id = get_usu_id(my_user)
    ok = actualizar_nota(not_id, data.titulo, data.contenido, usu_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return {"mensaje": "Nota actualizada"}


@router.delete("/notas/{not_id}")
def eliminar_nota_endpoint(
    not_id: int,
    my_user: Annotated[dict, Depends(get_current_user)],
):
    usu_id = get_usu_id(my_user)
    ok = eliminar_nota(not_id, usu_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return {"mensaje": "Nota eliminada"}
