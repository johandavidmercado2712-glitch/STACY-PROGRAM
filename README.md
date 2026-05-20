# STACY-PROGRAM
Sistema para capturar, consultar y exponer el historial de comandos de terminal mediante CLI y API con FastAPI.

## Descripción
`STACY-PROGRAM` obtiene comandos ejecutados en terminal (Linux/macOS/Windows), les agrega metadata y permite:
- Consultarlos desde consola.
- Exponerlos vía API REST.
- Guardarlos en base de datos MySQL.

## Requisitos
- Python 3.8+
- MySQL accesible desde tu entorno
- `pip`

## Dependencias
Instaladas desde `backend/requirements.txt`:
- fastapi
- uvicorn
- psutil
- mysql-connector-python
- python-dotenv

## Instalación
```bash
cd backend
pip install -r requirements.txt
Configuración de entorno
Crea o edita backend/.env con:
SECRET_KEY=STACY
DB_HOST=172.30.48.1
DB_USER=root
DB_PASSWORD=
DB_PORT=3307
DB_NAME=proyecto_gwen

Notas:
- Si tu MySQL está local en tu misma máquina, usa DB_HOST=localhost.
- Evita duplicar variables (por ejemplo, dos veces DB_HOST).

Ejecución
1) Modo consola (últimos comandos)
python TerminalComando.py
2) Modo consola (historial completo)
python TerminalComandoCompleto.py
3) API web (FastAPI)

uvicorn main:app --reload

Servidor local:
- http://127.0.0.1:8000

Endpoints disponibles
- GET /  

Respuesta básica de estado.
- GET /historial/ultimos  

Devuelve los últimos comandos (lógica actual limitada a 11).
- GET /historial/todos  

Devuelve todo el historial disponible.
Pruebas rápidas con curl

curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/historial/ultimos
curl http://127.0.0.1:8000/historial/todos

Estructura del proyecto
backend/
├── app/
│   ├── controllers/
│   ├── models/
│   └── views/
├── config/
│   └── db.py
├── routes/
├── public/
├── main.py
├── TerminalComando.py
├── TerminalComandoCompleto.py
└── requirements.txt

Notas técnicas
- En zsh, el historial puede traer prefijos tipo : 1779293328:0;.
- La app puede limpiarlos para guardar solo el comando real.
- La fecha que se guarda actualmente se genera al momento de procesar cada comando.

Tecnologías
- Python
- FastAPI
- MySQL
- Arquitectura tipo MVC