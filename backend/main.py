from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse  # para mandar respuestas en formato JSON
from pydantic import BaseModel
from typing_extensions import Annotated

from app.controllers.historial_controller import (
    HistorialControlador,
    HistorialControladorCompleto,
)
from auth.auth import get_current_user
from auth.auth import router as auth_router
from routes.carpetas import router as carpetas_router
from config.db import DB_CONFIG, guardar_comandos_nuevos, obtener_comando_por_nombre, obtener_comandos, reclamar_comandos_sin_usuario, importar_comandos
from config.carpetasBD import crear_tablas_carpetas
from config.usuarioDB import obtener_usuario_por_username
from mysql.connector import Error, connect

app = FastAPI(title="Historial de Comandos API", version="1.0.0")
app.include_router(auth_router)
app.include_router(carpetas_router)
crear_tablas_carpetas()
origins =[
    "http://localhost:8000",
    "http://localhost:5000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501",
    "http://52.87.195.200:5500",
    "http://52.87.195.200:8000",
    
]

def get_usu_id(my_user: dict) -> int:
    user = obtener_usuario_por_username(my_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user["USU_ID"]

@app.get("/users/profile")
def profile(my_user: Annotated[dict, Depends(get_current_user)]):
    return my_user


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def principal():
    return {"mensaje": "API de Historial de Comandos"}


@app.get("/historial/ultimos")
def obtener_ultimos_comandos(my_user: Annotated[dict, Depends(get_current_user)]):
    usu_id = get_usu_id(my_user)
    reclamar_comandos_sin_usuario(usu_id)
    try:
        controlador = HistorialControlador()
        modelo = controlador.modelo
        comandos = modelo.obtener_desde_fc()
        if not comandos:
            comandos = modelo.obtener_desde_archivo()

        if comandos:
            existentes = obtener_comandos(usu_id=usu_id)
            ts_map = {c["COM_NOMBRE"]: c["COM_FECHA"] for c in existentes}
            guardar_comandos_nuevos(comandos, ts_map, usu_id=usu_id)

        db_comandos = obtener_comandos(usu_id=usu_id)
        db_comandos.reverse()
        ultimos = db_comandos[-11:] if len(db_comandos) > 11 else db_comandos
        ultimos.reverse()

        resultado = []
        for c in ultimos:
            fecha = c["COM_FECHA"]
            if hasattr(fecha, "strftime"):
                fecha = fecha.strftime("%Y-%m-%d %H:%M:%S")
            resultado.append({
                "com_id": c["COM_ID"],
                "comando": c["COM_NOMBRE"],
                "fecha": fecha,
                "ruta": c["COM_RUTA"] or "",
            })

        return {"estado": "éxito", "total": len(resultado), "comandos": resultado}
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"estado": "error", "mensaje": str(e)}
        )


@app.get("/historial/todos")
def obtener_todos_comandos(my_user: Annotated[dict, Depends(get_current_user)]):
    usu_id = get_usu_id(my_user)
    reclamar_comandos_sin_usuario(usu_id)
    try:
        controlador = HistorialControladorCompleto()
        modelo = controlador.modelo
        comandos = modelo.obtener_todo_desde_fc()
        if not comandos:
            comandos = modelo.obtener_todo_desde_archivo()

        if comandos:
            existentes = obtener_comandos(usu_id=usu_id)
            ts_map = {c["COM_NOMBRE"]: c["COM_FECHA"] for c in existentes}
            guardar_comandos_nuevos(comandos, ts_map, usu_id=usu_id)

        db_comandos = obtener_comandos(usu_id=usu_id)

        resultado = []
        for c in db_comandos:
            fecha = c["COM_FECHA"]
            if hasattr(fecha, "strftime"):
                fecha = fecha.strftime("%Y-%m-%d %H:%M:%S")
            resultado.append({
                "com_id": c["COM_ID"],
                "comando": c["COM_NOMBRE"],
                "fecha": fecha,
                "ruta": c["COM_RUTA"] or "",
            })

        return {"estado": "éxito", "total": len(resultado), "comandos": resultado}
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"estado": "error", "mensaje": str(e)}
        )
        
        
@app.get("/historial/comandos/{com_nombre}")
def buscar_comando_nombre(com_nombre: str, my_user: Annotated[dict, Depends(get_current_user)]):
    usu_id = get_usu_id(my_user)
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM comandos WHERE COM_NOMBRE = %s AND (USU_ID = %s OR USU_ID IS NULL) ORDER BY COM_ID DESC", (com_nombre, usu_id),
        )

        comandos = cursor.fetchall()
        cursor.close()
        conexion.close()
        if not comandos:
            return JSONResponse(
                status_code=404,
                content={"Estado": "Error", "Mensaje": "No Se Encontro El Comando"},
            )
        return{
            "Estado": "Exitoso",
            "Total": len(comandos),
            "comandos": comandos,
        }
    except Error as e:
        return JSONResponse(
            status_code=500, content={"Estado":"Error", "Mensaje": str(e)}
        )
        
class ComandoImportar(BaseModel):
    comando: str
    ruta: str = ""
    fecha: str | None = None

class ImportarRequest(BaseModel):
    comandos: list[ComandoImportar]


@app.post("/comandos/importar")
def importar_comandos_endpoint(
    data: ImportarRequest,
    my_user: Annotated[dict, Depends(get_current_user)],
):
    usu_id = get_usu_id(my_user)
    total = importar_comandos(
        [c.model_dump() for c in data.comandos], usu_id
    )
    return {"estado": "éxito", "importados": total}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
