"""Baseline del contrato de la API de STACY.

Guarda codigo + hash del cuerpo de cada ruta. Tras un cambio, el mismo
script falla si algo difiere (test de regresion real, no a ojo).

Uso:
  python3 baseline-api.py save   # guarda api-contract.baseline.json
  python3 baseline-api.py check  # compara contra el baseline, exit 1 si difiere
"""
import hashlib
import json
import sys
import urllib.request
import urllib.error

BASE = 'https://stacyprogram.online'

RUTAS = [
    ('GET', '/', None),
    ('GET', '/api', None),
    ('GET', '/salud', None),
    ('GET', '/docs', None),
    ('POST', '/token', b''),
    ('POST', '/register', b'{}'),
    ('GET', '/carpetas', None),
    ('GET', '/notas', None),
    ('GET', '/users/profile', None),
    ('GET', '/historial/ultimos', None),
    ('GET', '/historial/todos', None),
    ('GET', '/comandos/importar', None),
    ('GET', '/auth/google/login?port=1234', None),
    ('GET', '/openapi.json', None),
]

ARCHIVO = 'api-contract.baseline.json'


def pedir(metodo, ruta, cuerpo):
    url = BASE + ruta

    class SinRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(SinRedirect)
    req = urllib.request.Request(url, data=cuerpo, method=metodo)
    if cuerpo is not None:
        req.add_header('Content-Type', 'application/json')
    try:
        with opener.open(req, timeout=20) as resp:
            cuerpo_resp = resp.read()
            return resp.status, cuerpo_resp, dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def snapshot():
    estado = {}
    for metodo, ruta, cuerpo in RUTAS:
        codigo, resp, cabeceras = pedir(metodo, ruta, cuerpo)
        # Normalizar: quitar cabeceras volatiles (fechas, ids de request)
        cabs = {k: v for k, v in cabeceras.items()
                if k.lower() not in ('date', 'x-vercel-id', 'x-vercel-cache',
                                     'set-cookie', 'server-timing')}
        # Para /auth/google/login solo importa el destino del 302, no el state aleatorio
        if ruta.startswith('/auth/google/login') and codigo in (302, 307):
            loc = cabs.get('Location', '')
            firma = loc.split('state=')[0] if 'state=' in loc else loc
        else:
            firma = hashlib.sha256(resp).hexdigest()[:16]
        estado[f'{metodo} {ruta}'] = {'codigo': codigo, 'firma': firma}
        print(f'  {metodo} {ruta} -> {codigo} [{firma}]')
    return estado


def main():
    accion = sys.argv[1] if len(sys.argv) > 1 else 'check'
    print(f'Baseline API contra {BASE} ...')
    actual = snapshot()
    if accion == 'save':
        with open(ARCHIVO, 'w') as f:
            json.dump(actual, f, indent=2)
        print(f'Guardado en {ARCHIVO}')
        return
    with open(ARCHIVO) as f:
        esperado = json.load(f)
    fallos = []
    for clave, ref in esperado.items():
        got = actual.get(clave)
        if got != ref:
            fallos.append(f'{clave}: esperado {ref}, obtenido {got}')
    for clave in actual:
        if clave not in esperado:
            fallos.append(f'{clave}: ruta nueva no registrada en baseline')
    if fallos:
        print('DIFERENCIAS DETECTADAS:')
        for f_ in fallos:
            print(f'  ✗ {f_}')
        sys.exit(1)
    print(f'OK: {len(esperado)} rutas identicas al baseline.')


if __name__ == '__main__':
    main()
