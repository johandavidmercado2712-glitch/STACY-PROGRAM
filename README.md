# STACY-PROGRAM

Sistema de gestión de historial de comandos para terminal.

## Descripción

STACY-PROGRAM permite capturar y mostrar el historial de comandos ejecutados en tu terminal (bash, zsh, PowerShell).

## Requisitos

- Python 3.8+
- FastAPI (para API web)
- Uvicorn (servidor)

## Instalación

```bash
cd backend
pip install -r requirements.txt
```

## Uso

### Consola (limitado - 11 comandos)

```bash
python TerminalComando.py
```

### Consola (historial completo)

```bash
python TerminalComandoCompleto.py
```

### API Web (FastAPI)

```bash
uvicorn main:app --reload
```

Luego accede a: http://127.0.0.1:8000/historialComandos

## Estructura

```
backend/
├── app/
│   ├── controllers/
│   ├── models/
│   └── views/
├── config/
├── routes/
├── public/
├── TerminalComando.py        # CLI (11 comandos)
├── TerminalComandoCompleto.py # CLI (completo)
└── main.py                   # API FastAPI
```

## Tecnologías

- Python
- FastAPI
- MVC Patrón