import os #leer entornos, variables virtuales 
from mysql.connector import connect, Error 
from dotenv import load_dotenv #cargar el el archio env. y mira sus datos

load_dotenv() #cargar la informacion del archivo env

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
                COM_RUTA TEXT,
                USU_ID INT DEFAULT NULL
            )
        """)
        try:
            cursor.execute("ALTER TABLE comandos ADD COLUMN USU_ID INT DEFAULT NULL")
            conexion.commit()
        except Error:
            pass
        conexion.commit()
        cursor.close()
        conexion.close()
    except Error as e:
        print(f"Error al crear tabla: {e}")


def guardar_comando(comando: str, ruta: str, usu_id: int = None):
    """Guarda un comando en la base de datos usando fecha de MySQL."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO comandos (COM_NOMBRE, COM_FECHA, COM_RUTA, USU_ID)
            VALUES (%s, NOW(), %s, %s) 
            """,
            (comando, ruta, usu_id),
        )

        conexion.commit()
        print(f"Comando guardado en BD: {comando}")
        cursor.close()
        conexion.close()
        return True

    except Error as e:
        print(f"Error al guardar en BD: {e}")
        return False


def guardar_comandos_nuevos(comandos, ts_map, usu_id: int = None):
    """Guarda solo los comandos que aún no están en ts_map, con timestamps escalonados."""
    nuevos = [c for c in comandos if isinstance(c, dict) and c.get("comando", "") not in ts_map]
    if not nuevos:
        return
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        for i, cmd in enumerate(nuevos):
            cursor.execute(
                "INSERT INTO comandos (COM_NOMBRE, COM_FECHA, COM_RUTA, USU_ID) VALUES (%s, DATE_SUB(NOW(), INTERVAL %s SECOND), %s, %s)",
                (cmd["comando"], i * 2, cmd.get("ruta", ""), usu_id),
            )
            ts_map[cmd["comando"]] = None
        conexion.commit()
        cursor.close()
        conexion.close()
    except Error as e:
        print(f"Error al guardar comandos nuevos: {e}")


def obtener_comando_por_nombre(nombre, usu_id: int = None):
    """Obtiene el registro más reciente de un comando por nombre."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        if usu_id:
            cursor.execute(
                "SELECT * FROM comandos WHERE COM_NOMBRE = %s AND (USU_ID = %s OR USU_ID IS NULL) ORDER BY COM_ID DESC LIMIT 1",
                (nombre, usu_id),
            )
        else:
            cursor.execute(
                "SELECT * FROM comandos WHERE COM_NOMBRE = %s ORDER BY COM_ID DESC LIMIT 1",
                (nombre,),
            )
        comando = cursor.fetchone()
        cursor.close()
        conexion.close()
        return comando
    except Error as e:
        print(f"Error al buscar comando: {e}")
        return None


def obtener_comandos(limite: int = None, usu_id: int = None):
    """Obtiene comandos de la base de datos, opcionalmente filtrados por usuario."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)

        if usu_id:
            if limite:
                cursor.execute(
                    "SELECT * FROM comandos WHERE USU_ID = %s OR USU_ID IS NULL ORDER BY COM_ID DESC LIMIT %s",
                    (usu_id, limite),
                )
            else:
                cursor.execute(
                    "SELECT * FROM comandos WHERE USU_ID = %s OR USU_ID IS NULL ORDER BY COM_ID DESC",
                    (usu_id,),
                )
        else:
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
        return comandos

    except Error as e:
        print(f"Error al obtener comandos: {e}")
        return []


# Crear tabla al importar
crear_tabla()
