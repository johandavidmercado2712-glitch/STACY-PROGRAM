from mysql.connector import Error, connect


from config.db import DB_CONFIG


def crear_tabla_usuarios():
    """Crea la tabla de usuarios si no existe."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                USU_ID INT(11) NOT NULL AUTO_INCREMENT,
                USU_USERNAME VARCHAR(50) NOT NULL,
                USU_APELLIDOS VARCHAR(120) NOT NULL,
                USU_CORREO VARCHAR(120) NOT NULL,
                USU_PASSWORD_HASH VARCHAR(255) NOT NULL,
                USU_ACTIVO TINYINT(1) NOT NULL DEFAULT 1,
                USU_CREATED_AT DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                USU_UPDATED_AT TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (USU_ID),
                UNIQUE KEY USU_USERNAME (USU_USERNAME),
                UNIQUE KEY USU_CORREO (USU_CORREO)
            )
            """
        )
        conexion.commit()
    except Error as e:
        print(f"Error al crear tabla usuarios: {e}")
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def guardar_usuario(username: str, apellidos: str, correo: str, password_hash: str, activo: int = 1):
    """Guarda un usuario en la base de datos."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO usuarios (USU_USERNAME, USU_APELLIDOS, USU_CORREO, USU_PASSWORD_HASH, USU_ACTIVO)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (username, apellidos, correo, password_hash, activo),
        )
        conexion.commit()
        return True
    except Error as e:
        print(f"Error al guardar usuario: {e}")
        return False
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def obtener_usuarios(limite: int = None):
    """Obtiene usuarios de la base de datos."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        if limite:
            cursor.execute("SELECT * FROM usuarios ORDER BY USU_ID DESC LIMIT %s", (limite,))
        else:
            cursor.execute("SELECT * FROM usuarios ORDER BY USU_ID DESC")
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener usuarios: {e}")
        return []
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def obtener_usuario_por_username(username: str):
    """Obtiene un usuario activo por username."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT USU_ID, USU_USERNAME, USU_APELLIDOS, USU_CORREO, USU_PASSWORD_HASH, USU_ACTIVO, USU_CREATED_AT
            FROM usuarios
            WHERE USU_USERNAME = %s
            LIMIT 1
            """,
            (username,),
        )
        return cursor.fetchone()
    except Error as e:
        print(f"Error al buscar usuario por username: {e}")
        return None
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass
