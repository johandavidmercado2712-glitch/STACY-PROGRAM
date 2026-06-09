from mysql.connector import Error, connect
from config.db import DB_CONFIG


def crear_tabla_notas():
    """Crea la tabla de notas si no existe."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notas (
                NOT_ID INT AUTO_INCREMENT PRIMARY KEY,
                NOT_TITULO VARCHAR(200) NOT NULL,
                NOT_CONTENIDO TEXT,
                USU_ID INT NOT NULL,
                NOT_CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP,
                NOT_UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (USU_ID) REFERENCES usuarios(USU_ID)
            )
            """
        )
        conexion.commit()
    except Error as e:
        print(f"Error al crear tabla notas: {e}")
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def guardar_nota(titulo: str, contenido: str, usu_id: int):
    """Guarda una nota en la base de datos."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO notas (NOT_TITULO, NOT_CONTENIDO, USU_ID)
            VALUES (%s, %s, %s)
            """,
            (titulo, contenido, usu_id),
        )
        conexion.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al guardar nota: {e}")
        return None
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def obtener_notas(usu_id: int):
    """Obtiene todas las notas de un usuario."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT NOT_ID, NOT_TITULO, NOT_CONTENIDO, NOT_CREATED_AT, NOT_UPDATED_AT FROM notas WHERE USU_ID = %s ORDER BY NOT_UPDATED_AT DESC",
            (usu_id,),
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener notas: {e}")
        return []
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def obtener_nota_por_id(not_id: int, usu_id: int):
    """Obtiene una nota por su ID, solo si pertenece al usuario."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT NOT_ID, NOT_TITULO, NOT_CONTENIDO, NOT_CREATED_AT, NOT_UPDATED_AT FROM notas WHERE NOT_ID = %s AND USU_ID = %s",
            (not_id, usu_id),
        )
        return cursor.fetchone()
    except Error as e:
        print(f"Error al buscar nota por ID: {e}")
        return None
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def actualizar_nota(not_id: int, titulo: str, contenido: str, usu_id: int):
    """Actualiza titulo y contenido de una nota, solo si pertenece al usuario."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE notas SET NOT_TITULO = %s, NOT_CONTENIDO = %s WHERE NOT_ID = %s AND USU_ID = %s",
            (titulo, contenido, not_id, usu_id),
        )
        conexion.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error al actualizar nota: {e}")
        return False
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def eliminar_nota(not_id: int, usu_id: int):
    """Elimina una nota, solo si pertenece al usuario."""
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute(
            "DELETE FROM notas WHERE NOT_ID = %s AND USU_ID = %s",
            (not_id, usu_id),
        )
        conexion.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error al eliminar nota: {e}")
        return False
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass
