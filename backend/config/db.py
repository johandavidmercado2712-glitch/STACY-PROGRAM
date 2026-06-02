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
        conexion = connect(**DB_CONFIG) #el ** desempaqueta el paquete es decir la informacion que esta en DB_CONFIG para no escribir otra vez sus datos
        cursor = conexion.cursor() #para ejecutar ordenes 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comandos (                 
                COM_ID INT AUTO_INCREMENT PRIMARY KEY,
                COM_NOMBRE TEXT,
                COM_FECHA DATETIME,
                COM_RUTA TEXT
            )
        """)
        conexion.commit()#guardar cambios
        cursor.close() #cerrar Conexion
        conexion.close()
    except Error as e:
        print(f"Error al crear tabla: {e}")


def guardar_comando(comando: str, ruta: str):
    """Guarda un comando en la base de datos usando fecha de MySQL."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO comandos (COM_NOMBRE, COM_FECHA, COM_RUTA)
            VALUES (%s, NOW(), %s) 
            """, #el %s es para evitas inyecciones sql y el NOW() es para colocar la fecha actual
            (comando, ruta),
        )

        conexion.commit()
        print(f"✅ Comando guardado en BD: {comando}")
        cursor.close()
        conexion.close()
        return True

    except Error as e:
        print(f"❌ Error al guardar en BD: {e}")
        return False


def guardar_comandos_nuevos(comandos, ts_map):
    """Guarda solo los comandos que aún no están en ts_map, con timestamps escalonados."""
    nuevos = [c for c in comandos if isinstance(c, dict) and c.get("comando", "") not in ts_map]
    if not nuevos:
        return
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        for i, cmd in enumerate(nuevos):
            cursor.execute(
                "INSERT INTO comandos (COM_NOMBRE, COM_FECHA, COM_RUTA) VALUES (%s, DATE_SUB(NOW(), INTERVAL %s SECOND), %s)",
                (cmd["comando"], i * 2, cmd.get("ruta", "")),
            )
            ts_map[cmd["comando"]] = None
        conexion.commit()
        cursor.close()
        conexion.close()
    except Error as e:
        print(f"Error al guardar comandos nuevos: {e}")


def obtener_comando_por_nombre(nombre):
    """Obtiene el registro más reciente de un comando por nombre."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
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


def obtener_comandos(limite: int = None):
    """Obtiene comandos de la base de datos."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True) #al momento de ponerlo True recibe los datos como un diccionario 

        if limite: #si el usuario puso un limite extrae solo los que pidio el usuario 
            cursor.execute(
                "SELECT * FROM comandos ORDER BY COM_ID DESC LIMIT %s",
                (limite,),
            )
        else: #sino lo extrae todos 
            cursor.execute("SELECT * FROM comandos ORDER BY COM_ID DESC")

        comandos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return comandos

    except Error as e:
        print(f"❌ Error al obtener comandos: {e}")
        return []


# Crear tabla al importar
crear_tabla()
