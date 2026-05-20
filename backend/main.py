from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.controllers.historial_controller import (
    HistorialControlador,
    HistorialControladorCompleto,
)
from config.db import DB_CONFIG
from mysql.connector import connect, Error

app = FastAPI(title="Historial de Comandos API", version="1.0.0")


@app.get("/")
def read_root():
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
