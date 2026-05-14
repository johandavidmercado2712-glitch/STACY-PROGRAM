from fastapi import FastAPI
from app.controllers.historial_controller import HistorialControlador

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/historial")
async def get_historial():
    controlador = HistorialControlador()
    controlador.ejecutar()
    return {"message": "Historial mostrado en consola"}