"""
Pruebas del endpoint de notificaciones.

Enfoque:
  * No mutan datos ni necesitan un usuario real.
  * Detectan exactamente el fallo que provocaba el 500: la tabla
    `notificaciones` inexistente en producción.
  * Verifican que las rutas nuevas de aceptar/rechazar estén registradas.

Ejecutar:
    cd STACY-PROGRAM
    python -m unittest backend/tests/test_notificaciones.py -v
"""

import os
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BACKEND = RAIZ / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from routes.web import app  # noqa: E402

cliente = TestClient(app)


class RutasNotificaciones(unittest.TestCase):
    def test_get_sin_token_no_devuelve_500(self):
        """Sin credenciales debe ser 401/403, nunca 500."""
        respuesta = cliente.get("/notificaciones")
        self.assertIn(respuesta.status_code, (401, 403))

    def test_rutas_aceptar_y_rechazar_registradas(self):
        rutas = set(cliente.get("/openapi.json").json()["paths"])
        self.assertIn("/notificaciones/{id_notificacion}/aceptar", rutas)
        self.assertIn("/notificaciones/{id_notificacion}/rechazar", rutas)

    def test_openapi_incluye_el_endpoint(self):
        spec = cliente.get("/openapi.json").json()
        self.assertIn("/notificaciones", spec["paths"])


@unittest.skipUnless(
    os.environ.get("DATABASE_URL") or os.environ.get("STACY_TEST_DATABASE_URL"),
    "requiere DATABASE_URL para comprobar el esquema real",
)
class EsquemaProduccion(unittest.TestCase):
    def test_tabla_notificaciones_existe_con_sus_columnas(self):
        import psycopg2

        url = os.environ.get("DATABASE_URL") or os.environ["STACY_TEST_DATABASE_URL"]
        with psycopg2.connect(url) as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT column_name FROM information_schema.columns"
                " WHERE table_name = 'notificaciones'"
            )
            columnas = {fila[0] for fila in cursor.fetchall()}

        esperadas = {
            "id",
            "id_usuario",
            "titulo",
            "mensaje",
            "tipo",
            "de",
            "url",
            "estado",
            "fecha_creacion",
        }
        self.assertTrue(
            esperadas.issubset(columnas),
            f"faltan columnas en notificaciones: {esperadas - columnas}",
        )


if __name__ == "__main__":
    unittest.main()
