from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse  # para mandar respuestas en formato JSON
from typing_extensions import Annotated

from app.controllers.historial_controller import (
    HistorialControlador,
    HistorialControladorCompleto,
)
from auth.auth import get_current_user
from auth.auth import router as auth_router
from config.db import DB_CONFIG  # tra la configuracion de la base de datos
from mysql.connector import Error, connect  # extrae las herramientas de mysql

app = FastAPI(title="Historial de Comandos API", version="1.0.0") #encargado de manejar todas las rutas 
app.include_router(auth_router)
origins =[
    "http://localhost:8000",
    "http://localhost:5000",
    "http://localhost:5500",
    "http://127.0.0.1:5500"
    
]

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
def obtener_ultimos_comandos():
    """Retorna los últimos 11 comandos."""
    try:
        controlador = HistorialControlador()
        modelo = controlador.modelo
        comandos = modelo.obtener_desde_fc()
        if not comandos:
            comandos = modelo.obtener_desde_archivo()
        return {
            "estado": "éxito",
            "total": len(comandos),
            "comandos": comandos,
        }
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"estado": "error", "mensaje": str(e)}
        )


@app.get("/historial/todos")
def obtener_todos_comandos():
    """Retorna todo el historial de comandos."""
    try:
        controlador = HistorialControladorCompleto()
        modelo = controlador.modelo
        comandos = modelo.obtener_todo_desde_fc()
        if not comandos:
            comandos = modelo.obtener_todo_desde_archivo()
        return {
            "estado": "éxito",
            "total": len(comandos),
            "comandos": comandos,
        }
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"estado": "error", "mensaje": str(e)}
        )
        
        
@app.get("/historial/comandos/{com_nombre}")
def buscar_comando_nombre(com_nombre:str):
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM comandos WHERE COM_NOMBRE= %s ORDER BY COM_ID DESC", (com_nombre,),
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
        
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
