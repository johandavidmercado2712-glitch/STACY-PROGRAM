from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
from fastapi.responses import JSONResponse  # para mandar respuestas en formato JSON
from pydantic import BaseModel
=======
from fastapi.responses import JSONResponse
>>>>>>> 99aec01 (Implementacion De Seguridad)
from typing_extensions import Annotated
from mysql.connector import Error, connect
from pydantic import BaseModel

<<<<<<< HEAD
from auth.auth import get_current_user
from auth.auth import router as auth_router
from routes.carpetas import router as carpetas_router
from routes.notas import router as notas_router
from routes.google_auth import router as google_auth_router
from config.db import DB_CONFIG, obtener_comando_por_nombre, obtener_comandos, importar_comandos, actualizar_comando_por_id
from config.carpetasBD import crear_tablas_carpetas
from config.notasBD import crear_tabla_notas
from config.usuarioDB import obtener_usuario_por_username
from mysql.connector import Error, connect

app = FastAPI(title="Historial de Comandos API", version="1.0.0")
app.include_router(auth_router)
app.include_router(carpetas_router)
app.include_router(notas_router)
app.include_router(google_auth_router)
crear_tablas_carpetas()
crear_tabla_notas()
origins =[
=======
from app.models.historial_modelo import HistorialModelo, HistorialModeloCompleto
from auth.auth import get_current_user
from auth.auth import router as auth_router
from routes.carpetas import router as carpetas_router
from config.db import DB_CONFIG, guardar_comandos_nuevos, obtener_comando_por_nombre, obtener_comandos, guardar_comando
from config.usuarioDB import crear_tabla_usuarios
from config.carpetasBD import crear_tablas_carpetas

app = FastAPI(title="Historial de Comandos API", version="1.0.0") #se crea la aplicacion
app.include_router(auth_router) #trae los enpoint de esa direccion
app.include_router(carpetas_router)
crear_tabla_usuarios()   # se crea primero para que carpetas pueda referenciarla
crear_tablas_carpetas() #ejecuta esta funcion de la DB cuando se inicia el servidor 

origins = [
>>>>>>> 99aec01 (Implementacion De Seguridad)
    "http://localhost:8000",
    "http://localhost:5000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
<<<<<<< HEAD
    "http://127.0.0.1:5501",
    "http://52.87.195.200:5500",
    "http://52.87.195.200:8000",
    "http://stacyprogram.online",
    "http://stacyprogram.online:8000",
]

def get_usu_id(my_user: dict) -> int:
    user = obtener_usuario_por_username(my_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user["USU_ID"]

@app.get("/users/profile")
def profile(my_user: Annotated[dict, Depends(get_current_user)]):
    user = obtener_usuario_por_username(my_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "username": user["USU_USERNAME"],
        "apellidos": user["USU_APELLIDOS"],
        "correo": user["USU_CORREO"],
        "activo": user["USU_ACTIVO"],
        "created_at": str(user.get("USU_CREATED_AT", "")) if hasattr(user.get("USU_CREATED_AT"), "strftime") else (user.get("USU_CREATED_AT") or ""),
    }


=======
    "http://52.87.195.200:8080",
    "http://ec2-52-87-195-200.compute-1.amazonaws.com:8000",
    "http://ec2-52-87-195-200.compute-1.amazonaws.com:8080",
]

>>>>>>> 99aec01 (Implementacion De Seguridad)
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


<<<<<<< HEAD
@app.get("/historial/ultimos")
def obtener_ultimos_comandos(my_user: Annotated[dict, Depends(get_current_user)]):
    usu_id = get_usu_id(my_user)
    try:
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

=======
@app.get("/users/profile")
def profile(my_user: Annotated[dict, Depends(get_current_user)]):#sin un token valido no podra ver el perfil
    return my_user


def _formatear_fecha(fecha):
    if isinstance(fecha, str):
        return fecha
    if hasattr(fecha, "strftime"):
        return fecha.strftime("%Y-%m-%d %H:%M:%S")
    return None #formatea la fecha de la base de datos para que este en ano, mes , dia 


def _procesar_comandos(limite=None):
    try:
        if limite:
            modelo = HistorialModelo()#instancia historialModelo para utilizar sus metodos 
            comandos = modelo.obtener_desde_fc() or modelo.obtener_desde_archivo()
        else:
            modelo = HistorialModeloCompleto()
            comandos = modelo.obtener_todo_desde_fc() or modelo.obtener_todo_desde_archivo()

        if not comandos:
            return {"estado": "éxito", "total": 0, "comandos": []}

        existentes = obtener_comandos() #trae los comandos que tengo guardadis en la BD
        ts_map = {c["COM_NOMBRE"]: c["COM_FECHA"] for c in existentes}  #es un diccionario donde estara almacenado los comandos en estilo cache para no hacer tantas consultas a mysql 

        guardar_comandos_nuevos(comandos, ts_map)

        existentes = obtener_comandos()
        id_map = {c["COM_NOMBRE"]: c["COM_ID"] for c in existentes} #compara los que tienes guardado en la base de datos y los que acaban de leer

        resultado = []
        for cmd in comandos:
            if not isinstance(cmd, dict): #el isinstance es para verificar que el  si tal dato es de ese tipo ejemplo (cmd, dict) si cmd es un diccionario si es cierto devuelve un True y sino un Else 
                continue #si el cmd no es un diccionario continua 
            nombre = cmd.get("comando", "")
            ruta = cmd.get("ruta", "")
            if not nombre:
                continue

            fecha = ts_map.get(nombre)
            if not fecha:
                comando_db = obtener_comando_por_nombre(nombre)
                fecha = comando_db["COM_FECHA"] if comando_db else None

            resultado.append({
                "com_id": id_map.get(nombre),
                "comando": nombre,
                "fecha": _formatear_fecha(fecha),
                "ruta": ruta,
            })

        if limite:
            resultado.reverse()

>>>>>>> 99aec01 (Implementacion De Seguridad)
        return {"estado": "éxito", "total": len(resultado), "comandos": resultado}
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"estado": "error", "mensaje": str(e)}
        )


@app.get("/historial/ultimos")
def obtener_ultimos_comandos(my_user: Annotated[dict, Depends(get_current_user)]):
    return _procesar_comandos(limite=11)


@app.get("/historial/todos")
def obtener_todos_comandos(my_user: Annotated[dict, Depends(get_current_user)]):
<<<<<<< HEAD
    usu_id = get_usu_id(my_user)
    try:
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
=======
    return _procesar_comandos()


@app.get("/historial/comandos/{com_nombre}")
def buscar_comando_nombre(com_nombre: str, my_user: Annotated[dict, Depends(get_current_user)]):
>>>>>>> 99aec01 (Implementacion De Seguridad)
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
<<<<<<< HEAD
            "SELECT * FROM comandos WHERE COM_NOMBRE = %s AND (USU_ID = %s OR USU_ID IS NULL) ORDER BY COM_ID DESC", (com_nombre, usu_id),
=======
            "SELECT * FROM comandos WHERE COM_NOMBRE = %s ORDER BY COM_ID DESC",
            (com_nombre,),
>>>>>>> 99aec01 (Implementacion De Seguridad)
        )
        comandos = cursor.fetchall()
        cursor.close()
        conexion.close()
        if not comandos:
            return JSONResponse(
                status_code=404,
                content={"estado": "error", "mensaje": "No se encontró el comando"},
            )
        return {"estado": "éxito", "total": len(comandos), "comandos": comandos}
    except Error as e:
        return JSONResponse(
            status_code=500, content={"estado": "error", "mensaje": str(e)}
        )
<<<<<<< HEAD
        
class ComandoImportar(BaseModel):
    comando: str
    ruta: str = ""
    fecha: str | None = None

class ImportarRequest(BaseModel):
    comandos: list[ComandoImportar]


@app.put("/comandos/{com_id}")
def editar_comando(
    com_id: int,
    data: ComandoImportar,
    my_user: Annotated[dict, Depends(get_current_user)],
):
    usu_id = get_usu_id(my_user)
    ok = actualizar_comando_por_id(com_id, data.comando, usu_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Comando no encontrado")
    return {"estado": "éxito", "mensaje": "Comando actualizado"}


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
=======


class RegistrarComandoRequest(BaseModel):
    comando: str
    ruta: str = ""


class ComandoSyncItem(BaseModel):
    comando: str
    ruta: str = ""


class RegistrarComandosBulkRequest(BaseModel):
    comandos: list[ComandoSyncItem]


@app.post("/historial/registrar")
def registrar_nuevo_comando(
    data: RegistrarComandoRequest,
    my_user: Annotated[dict, Depends(get_current_user)]
):
    ok = guardar_comando(data.comando, data.ruta)
    if not ok:
        raise HTTPException(status_code=500, detail="Error al registrar comando")
    return {"mensaje": "Comando registrado exitosamente"}


@app.post("/historial/registrar-bulk")
def registrar_comandos_bulk(
    data: RegistrarComandosBulkRequest,
    my_user: Annotated[dict, Depends(get_current_user)]
):
    try:
        comandos_dict = [{"comando": c.comando, "ruta": c.ruta} for c in data.comandos]
        existentes = obtener_comandos()
        ts_map = {c["COM_NOMBRE"]: c["COM_FECHA"] for c in existentes}
        guardar_comandos_nuevos(comandos_dict, ts_map)
        return {"estado": "éxito", "mensaje": f"{len(data.comandos)} comandos procesados"}
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"estado": "error", "mensaje": str(e)}
        )

>>>>>>> 99aec01 (Implementacion De Seguridad)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
