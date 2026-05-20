import os 
from datetime import datetime
from mysql.connector import connect, Error
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "port": os.getenv("DB_PORT"),
}


def crear_tabla():
    """Crea la tabla de comandos si no existe."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comandos (
                COM_ID INT AUTO_INCREMENT PRIMARY KEY,
                COM_NOMBRE TEXT,
                COM_FECHA DATETIME,
                COM_RUTA TEXT
            )
        """)
        conexion.commit()
        cursor.close()
        conexion.close()
    except Error as e:
        print(f"Error al crear tabla: {e}")


def guardar_comando(comando: str, ruta: str, fecha: str = None):
    """Guarda un comando en la base de datos."""
    if fecha is None:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO comandos (COM_NOMBRE, COM_FECHA, COM_RUTA)
            VALUES (%s, %s, %s)
            """,
            (comando, fecha, ruta),
        )

        conexion.commit()
        print(f"✅ Comando guardado en BD: {comando}")
        cursor.close()
        conexion.close()
        return True

    except Error as e:
        print(f"❌ Error al guardar en BD: {e}")
        return False


def obtener_comandos(limite: int = None):
    """Obtiene comandos de la base de datos."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)

        if limite:
            cursor.execute(
                "SELECT * FROM comandos ORDER BY COM_ID DESC LIMIT %s",
                (limite,),
            )
        else:
            cursor.execute("SELECT * FROM comandos ORDER BY COM_ID DESC")

        comandos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return list(reversed(comandos))

    except Error as e:
        print(f"❌ Error al obtener comandos: {e}")
        return []


# Crear tabla al importar
crear_tabla()
