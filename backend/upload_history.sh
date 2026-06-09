#!/bin/bash

# --- CONFIG ---
API_URL="http://52.87.195.200:8000"
TOKEN="<PON_TU_TOKEN_AQUI>"

HOSTNAME=$(hostname)
HISTFILE="${BASH_HISTFILE:-$HOME/.bash_history}"
[ ! -f "$HISTFILE" ] && HISTFILE="$HOME/.zsh_history"
[ ! -f "$HISTFILE" ] && { echo "No se encontró .bash_history ni .zsh_history"; exit 1; }

python3 -c "
import json, sys
hist = []
with open('$HISTFILE', 'r', errors='ignore') as f:
    for line in f:
        line = line.strip().rstrip('\n')
        if not line or line.startswith('#'):
            continue
        hist.append({
            'comando': line,
            'ruta': '[MAQUINA:${HOSTNAME}]',
            'fecha': None
        })
print(json.dumps({'comandos': hist}))
" | curl -s -X POST "$API_URL/comandos/importar" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    --data-binary @-

echo ""
