from mysql.connector import Error, connect
from config.db import DB_CONFIG


def crear_tablas_carpetas():
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS carpetas (
                CAR_ID INT(11) NOT NULL AUTO_INCREMENT,
                CAR_NOMBRE VARCHAR(100) NOT NULL,
                CAR_DESCRIPCION VARCHAR(300) NOT NULL,
                USU_ID INT NOT NULL,
                PRIMARY KEY (CAR_ID),
                FOREIGN KEY (USU_ID) REFERENCES usuarios(USU_ID)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS comando_carpeta (
                COM_ID INT NOT NULL,
                CAR_ID INT NOT NULL,
                CC_DESCRIPCION TEXT,
                PRIMARY KEY (COM_ID, CAR_ID),
                FOREIGN KEY (COM_ID) REFERENCES comandos(COM_ID),
                FOREIGN KEY (CAR_ID) REFERENCES carpetas(CAR_ID)
            )
            """
        )
        conexion.commit()
        try:
            cursor.execute("ALTER TABLE comando_carpeta ADD COLUMN CC_DESCRIPCION TEXT")
            conexion.commit()
        except Error:
            pass
    except Error as e:
        print(f"Error al crear tablas carpetas: {e}")
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def guardar_carpeta(nombre: str, descripcion: str, usu_id: int):
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO carpetas (CAR_NOMBRE, CAR_DESCRIPCION, USU_ID)
            VALUES (%s, %s, %s)
            """,
            (nombre, descripcion, usu_id),
        )
        conexion.commit()
        return True
    except Error as e:
        print(f"Error al guardar carpeta: {e}")
        return False
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def obtener_carpetas(usu_id):
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM carpetas WHERE USU_ID = %s",
            (usu_id,),
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener carpetas: {e}")
        return []
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def eliminar_carpeta(car_id, usu_id):
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute(
            "DELETE FROM comando_carpeta WHERE CAR_ID = %s",
            (car_id,),
        )
        cursor.execute(
            "DELETE FROM carpetas WHERE CAR_ID = %s AND USU_ID = %s",
            (car_id, usu_id),
        )
        conexion.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error al eliminar carpeta: {e}")
        return False
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def asignar_comando(car_id, com_id):
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO comando_carpeta (COM_ID, CAR_ID) VALUES (%s, %s)",
            (com_id, car_id),
        )
        conexion.commit()
        return True
    except Error as e:
        print(f"Error al asignar comando a carpeta: {e}")
        return False
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def desasignar_comando(car_id, com_id):
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute(
            "DELETE FROM comando_carpeta WHERE COM_ID = %s AND CAR_ID = %s",
            (com_id, car_id),
        )
        conexion.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error al desasignar comando de carpeta: {e}")
        return False
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def obtener_asignaciones(usu_id):
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT cc.COM_ID, cc.CAR_ID, cc.CC_DESCRIPCION FROM comando_carpeta cc
            JOIN carpetas c ON cc.CAR_ID = c.CAR_ID
            WHERE c.USU_ID = %s
            """,
            (usu_id,),
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener asignaciones: {e}")
        return []
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def actualizar_descripcion_comando(car_id, com_id, descripcion):
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE comando_carpeta SET CC_DESCRIPCION = %s WHERE COM_ID = %s AND CAR_ID = %s",
            (descripcion, com_id, car_id),
        )
        conexion.commit()
        return True
    except Error as e:
        print(f"Error al actualizar descripcion: {e}")
        return False
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass


def obtener_comandos_de_carpeta(car_id):
    try:
        conexion = connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT c.* FROM comandos c
            JOIN comando_carpeta cc ON c.COM_ID = cc.COM_ID
            WHERE cc.CAR_ID = %s
            """,
            (car_id,),
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener comandos de carpeta: {e}")
        return []
    finally:
        try:
            cursor.close()
            conexion.close()
        except Exception:
            pass
