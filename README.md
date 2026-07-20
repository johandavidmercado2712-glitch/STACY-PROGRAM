# STACY - Sistema de Historial de Comandos

API REST para capturar, almacenar y consultar el historial de comandos de terminal con autenticación JWT, OAuth2 con Google y organización por carpetas.

## Stack

- **Backend:** Python + FastAPI
- **Base de datos:** MySQL
- **Autenticación:** JWT (PBKDF2 + SHA256) y Google OAuth2
- **Frontend:** HTML + CSS + JavaScript vanilla

## Requisitos

- Python 3.12+
- MySQL 8.0+
- pip

## Instalación

```bash
git clone <tu-repo>
cd STACY-PROGRAM/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuración

Copia el archivo de entorno:

```bash
cp .env.example .env
```

Edita `.env` con tus datos:

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta para firmar JWT |
| `DB_HOST` | Host de MySQL |
| `DB_USER` | Usuario de MySQL |
| `DB_PASSWORD` | Contraseña de MySQL |
| `DB_PORT` | Puerto de MySQL (por defecto 3306) |
| `DB_NAME` | Nombre de la base de datos |
| `GOOGLE_CLIENT_ID` | Client ID de Google OAuth |
| `GOOGLE_CLIENT_SECRET` | Client Secret de Google OAuth |
| `GOOGLE_REDIRECT_URI` | URL de callback para Google OAuth |
| `FRONTEND_URL` | URL del frontend |

## Ejecución

### API

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Crear usuario desde consola

```bash
python crear_usuario.py
```

### CLI: últimos comandos

```bash
python TerminalComando.py
```

### CLI: historial completo

```bash
python TerminalComandoCompleto.py
```

## Endpoints

### Autenticación

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `POST` | `/token` | No | Login (form-data: username, password) |
| `POST` | `/register` | No | Registro de usuario |
| `GET` | `/auth/google/login` | No | Redirige a Google OAuth |
| `GET` | `/auth/google/callback` | No | Callback de Google OAuth |
| `POST` | `/auth/exchange` | No | Canjea código de un solo uso por el JWT (evita filtrarlo en la URL) |
| `POST` | `/auth/google/exchange` | No | Canjea código de Google (extensión VS Code) por el JWT |
| `GET` | `/users/profile` | Bearer | Perfil del usuario autenticado |

### Historial

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `GET` | `/` | No | Health check |
| `GET` | `/historial/ultimos` | Bearer | Últimos 11 comandos del usuario |
| `GET` | `/historial/todos` | Bearer | Todos los comandos del usuario |
| `GET` | `/historial/comandos/{nombre}` | Bearer | Buscar comando por nombre (propios o sin dueño) |
| `PUT` | `/comandos/{id}` | Bearer | Editar un comando propio |
| `POST` | `/comandos/importar` | Bearer | Importar comandos desde otro equipo |

### Carpetas

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `POST` | `/carpetas` | Bearer | Crear carpeta |
| `GET` | `/carpetas` | Bearer | Listar carpetas |
| `DELETE` | `/carpetas/{id}` | Bearer | Eliminar carpeta |
| `POST` | `/carpetas/asignar` | Bearer | Asignar comando a carpeta |
| `POST` | `/carpetas/desasignar` | Bearer | Desasignar comando |
| `PUT` | `/carpetas/descripcion` | Bearer | Actualizar descripción |
| `GET` | `/carpetas/asignaciones` | Bearer | Obtener asignaciones |
| `GET` | `/carpetas/{id}/comandos` | Bearer | Comandos de una carpeta |

### Notas

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `GET` | `/notas` | Bearer | Listar notas del usuario |
| `POST` | `/notas` | Bearer | Crear nota |
| `GET` | `/notas/{id}` | Bearer | Obtener nota propia |
| `PUT` | `/notas/{id}` | Bearer | Actualizar nota propia |
| `DELETE` | `/notas/{id}` | Bearer | Eliminar nota propia |

## Despliegue en producción

### Con systemd

Crear `/etc/systemd/system/stacy-api.service`:

```ini
[Unit]
Description=STACY API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/STACY-PROGRAM/backend
Environment=PATH=/home/ubuntu/STACY-PROGRAM/backend/venv/bin
ExecStart=/home/ubuntu/STACY-PROGRAM/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable stacy-api
sudo systemctl start stacy-api
```

## Estructura del proyecto

```
STACY-PROGRAM/
├── backend/
│   ├── app/
│   │   ├── controllers/     # Lógica de controladores
│   │   ├── models/          # Modelos de datos
│   │   └── views/           # Vistas de consola
│   ├── auth/
│   │   ├── auth.py          # JWT + Google OAuth
│   │   └── hashing.py       # PBKDF2 password hashing
│   ├── config/
│   │   ├── db.py            # Conexión MySQL y CRUD comandos
│   │   ├── usuarioDB.py     # CRUD usuarios
│   │   └── carpetasBD.py    # CRUD carpetas
│   ├── routes/
│   │   └── carpetas.py      # Endpoints de carpetas
│   ├── main.py              # Punto de entrada FastAPI
│   ├── crear_usuario.py     # Script para crear usuarios
│   ├── requirements.txt     # Dependencias
│   └── .env                 # Variables de entorno
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── js/
│       ├── api.js
│       ├── app.js
│       ├── auth.js
│       ├── commands.js
│       ├── folders.js
│       ├── state.js
│       └── theme.js
└── README.md
```

## Licencia

MIT
