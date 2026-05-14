from fastapi import FastAPI
from app.controllers.historial_controller import MostrarComandos, MostrarComandosCompletos

app = FastAPI()

# comandosJS = controlador.modelo.mostrar_comandos()
@app.get("/")
async def root():
    return {"message": "Hello World"} 

@app.get("/historialComandos")
async def read_commands():
    controlador = MostrarComandos()
    comandos = controlador.ejecutar() 
    return {"comandos": comandos}

@app.get("/historialComandosCompletos")
async def read_total_commands():
    controlador = MostrarComandosCompletos()
    comandos = controlador.ejecutar()
    return {"comandos": comandos}