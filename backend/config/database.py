"""
Conexión a PostgreSQL de STACY.

En local la URL viene por la variable DATABASE_URL, por ejemplo:
    DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/stacy

En Vercel (o Railway/Neon) copias el connection string en
Settings -> Environment Variables con el mismo nombre DATABASE_URL.
URLs de Neon/Vercel Postgres funcionan directo con psycopg2.
"""

import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

# Sin DATABASE_URL en producción no hay API posible: fallar temprano.
DATABASE_URL = os.environ.get("DATABASE_URL", "")
ES_PRODUCCION = os.environ.get("APP_ENV", "").lower() == "production"

if ES_PRODUCCION and not DATABASE_URL:
    raise RuntimeError("Configura DATABASE_URL en el entorno de producción.")


@contextmanager
def conexion():
    """Abre una conexión por petición y la cierra al salir del contexto."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                yield cursor
    finally:
        conn.close()
