from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.controllers.historial_controller import (
    HistorialControlador,
    HistorialControladorCompleto,
)

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
