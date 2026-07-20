from fastapi import APIRouter, Depends, HTTPException
from typing_extensions import Annotated
from pydantic import BaseModel

from auth.auth import get_current_user
from config.usuarioDB import obtener_usuario_por_username
from config.carpetasBD import (
    guardar_carpeta,
    obtener_carpetas,
    eliminar_carpeta,
    actualizar_carpeta,
    asignar_comando,
    desasignar_comando,
    obtener_asignaciones,
    obtener_comandos_de_carpeta,
    actualizar_descripcion_comando,
    verificar_propietario_carpeta,
    comando_es_del_usuario,
)

router = APIRouter()


class CrearCarpetaRequest(BaseModel):
    nombre: str
    descripcion: str = ""


class ActualizarCarpetaRequest(BaseModel):
    nombre: str
    descripcion: str = ""


class AsignarRequest(BaseModel):
    car_id: int
    com_id: int


class DescripcionRequest(BaseModel):
    car_id: int
    com_id: int
    descripcion: str = ""


def get_usu_id(my_user: dict) -> int: #el jwt no  trae el id x eso se estrae el nombre , se busca en la base de datos y se trae el id
    user = obtener_usuario_por_username(my_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user["USU_ID"]


@router.post("/carpetas")
def crear_carpeta(
    data: CrearCarpetaRequest,
    my_user: Annotated[dict, Depends(get_current_user)],#obliga a queel usuario arroje en la terminal el token en el encabezado o arroja error 
):
    usu_id = get_usu_id(my_user)
    ok = guardar_carpeta(data.nombre, data.descripcion, usu_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Error al crear carpeta")
    return {"mensaje": "Carpeta creada exitosamente"}


@router.get("/carpetas")
def listar_carpetas(my_user: Annotated[dict, Depends(get_current_user)]):
    usu_id = get_usu_id(my_user)
    carpetas = obtener_carpetas(usu_id)
    return {"carpetas": carpetas}


@router.put("/carpetas/{car_id}")
def editar_carpeta(
    car_id: int,
    data: ActualizarCarpetaRequest,
    my_user: Annotated[dict, Depends(get_current_user)],
):
    usu_id = get_usu_id(my_user)
    ok = actualizar_carpeta(car_id, data.nombre, data.descripcion, usu_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Carpeta no encontrada")
    return {"mensaje": "Carpeta actualizada"}


@router.delete("/carpetas/{car_id}")
def borrar_carpeta(
    car_id: int,
    my_user: Annotated[dict, Depends(get_current_user)], #define que va a ser un un dicionario y que primero tiene que ejecutarse el get_current_user
):
    usu_id = get_usu_id(my_user)
    if not verificar_propietario_carpeta(car_id, usu_id):
        raise HTTPException(status_code=403, detail="No autorizado para acceder a esta carpeta")
    ok = eliminar_carpeta(car_id, usu_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Carpeta no encontrada")
    return {"mensaje": "Carpeta eliminada"}


@router.post("/carpetas/asignar")
def asignar(
    data: AsignarRequest,
    my_user: Annotated[dict, Depends(get_current_user)],
):
    usu_id = get_usu_id(my_user)
    if not verificar_propietario_carpeta(data.car_id, usu_id):
        raise HTTPException(status_code=403, detail="No autorizado para acceder a esta carpeta")
    dueño = comando_es_del_usuario(data.com_id, usu_id)
    if dueño is None:
        raise HTTPException(status_code=404, detail="Comando no encontrado")
    if not dueño:
        raise HTTPException(status_code=403, detail="No autorizado para usar este comando")
    ok = asignar_comando(data.car_id, data.com_id)
    if not ok:
        raise HTTPException(status_code=500, detail="Error al asignar comando")
    return {"mensaje": "Comando asignado a la carpeta"}


@router.post("/carpetas/desasignar")
def desasignar(
    data: AsignarRequest,
    my_user: Annotated[dict, Depends(get_current_user)],
):
    usu_id = get_usu_id(my_user)
    if not verificar_propietario_carpeta(data.car_id, usu_id):
        raise HTTPException(status_code=403, detail="No autorizado para acceder a esta carpeta")
    dueño = comando_es_del_usuario(data.com_id, usu_id)
    if dueño is None:
        raise HTTPException(status_code=404, detail="Comando no encontrado")
    if not dueño:
        raise HTTPException(status_code=403, detail="No autorizado para usar este comando")
    ok = desasignar_comando(data.car_id, data.com_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Asignacion no encontrada")
    return {"mensaje": "Comando desasignado de la carpeta"}


@router.put("/carpetas/descripcion")
def actualizar_descripcion(
    data: DescripcionRequest,
    my_user: Annotated[dict, Depends(get_current_user)],
):
    usu_id = get_usu_id(my_user)
    if not verificar_propietario_carpeta(data.car_id, usu_id):
        raise HTTPException(status_code=403, detail="No autorizado para acceder a esta carpeta")
    dueño = comando_es_del_usuario(data.com_id, usu_id)
    if dueño is None:
        raise HTTPException(status_code=404, detail="Comando no encontrado")
    if not dueño:
        raise HTTPException(status_code=403, detail="No autorizado para usar este comando")
    ok = actualizar_descripcion_comando(data.car_id, data.com_id, data.descripcion)
    if not ok:
        raise HTTPException(status_code=404, detail="Asignacion no encontrada")
    return {"mensaje": "Descripcion actualizada"}


@router.get("/carpetas/asignaciones")
def listar_asignaciones(my_user: Annotated[dict, Depends(get_current_user)]):
    usu_id = get_usu_id(my_user)
    asignaciones = obtener_asignaciones(usu_id)
    return {"asignaciones": asignaciones}


@router.get("/carpetas/{car_id}/comandos")
def listar_comandos_de_carpeta(
    car_id: int,
    my_user: Annotated[dict, Depends(get_current_user)],
):
    usu_id = get_usu_id(my_user)
    comandos = obtener_comandos_de_carpeta(car_id, usu_id=usu_id)
    return {"comandos": comandos}
