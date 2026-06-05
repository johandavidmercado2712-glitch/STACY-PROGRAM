#!/bin/bash
# Upload local shell history to STACY
# Usage: ./upload_history.sh <API_TOKEN> [API_URL]
#   API_URL defaults to http://52.87.195.200:8000

TOKEN="$1"
API_URL="${2:-http://52.87.195.200:8000}"

if [ -z "$TOKEN" ]; then
    echo "Usage: $0 <API_TOKEN> [API_URL]"
    echo ""
    echo "1. Log in to STACY at http://52.87.195.200:5500"
    echo "2. Click 'Copy Token' button"
    echo "3. Run: bash $0 <PASTE_TOKEN_HERE>"
    exit 1
fi

# Detect history file
if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zsh_history" ]; then
    HISTORY_FILE="$HOME/.zsh_history"
elif [ -f "$HOME/.bash_history" ]; then
    HISTORY_FILE="$HOME/.bash_history"
else
    echo "No se encontró .bash_history ni .zsh_history"
    exit 1
fi

MAQUINA=$(hostname)
echo "Maquina detectada: $MAQUINA"
echo "Leyendo historial desde: $HISTORY_FILE"

# Read history, deduplicate, skip empty lines
COMMANDS=$(python3 -c "
import json, os

path = os.path.expanduser('$HISTORY_FILE')
maquina = '$MAQUINA'
if not os.path.exists(path):
    exit(1)

comandos = []
with open(path, errors='ignore') as f:
    seen = set()
    for line in f:
        line = line.strip()
        if not line:
            continue
        # Clean zsh prefix: ': <timestamp>:<duration>;'
        if line.startswith(': '):
            sep = line.find(';')
            if sep != -1 and sep + 1 < len(line):
                line = line[sep + 1:].strip()
        if not line or line in seen:
            continue
        seen.add(line)
        ruta = '[MAQUINA:' + maquina + '] ' + os.getcwd()
        comandos.append({'comando': line, 'ruta': ruta})

print(json.dumps({'comandos': comandos}))
")

if [ -z "$COMMANDS" ]; then
    echo "Error al leer el historial"
    exit 1
fi

COUNT=$(echo "$COMMANDS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)['comandos']))")
echo "Enviando $COUNT comandos a $API_URL/comandos/importar ..."

RESPONSE=$(curl -s -X POST "$API_URL/comandos/importar" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$COMMANDS")

echo "Respuesta: $RESPONSE"
