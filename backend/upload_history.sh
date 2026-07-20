#!/bin/bash

# --- CONFIG ---
API_URL="https://stacyprogram.online"
TOKEN="<PON_TU_TOKEN_AQUI>"

HOSTNAME_VAL=$(hostname)
HISTFILE="${BASH_HISTFILE:-$HOME/.bash_history}"
[ ! -f "$HISTFILE" ] && HISTFILE="$HOME/.zsh_history"
[ ! -f "$HISTFILE" ] && { echo "No se encontro .bash_history ni .zsh_history"; exit 1; }

# Valores por entorno (sin interpolacion en el codigo Python) => sin inyeccion de comandos.
STACY_HISTFILE="$HISTFILE" STACY_HOSTNAME="$HOSTNAME_VAL" python3 - <<'PY' | curl -s -X POST "$API_URL/comandos/importar" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    --data-binary @-
import json, os
hist = []
path = os.path.expanduser(os.environ['STACY_HISTFILE'])
maquina = os.environ['STACY_HOSTNAME']
with open(path, 'r', errors='ignore') as f:
    for line in f:
        line = line.strip().rstrip('\n')
        if not line or line.startswith('#'):
            continue
        hist.append({
            'comando': line,
            'ruta': '[MAQUINA:' + maquina + ']',
            'fecha': None
        })
print(json.dumps({'comandos': hist}))
PY

echo ""
