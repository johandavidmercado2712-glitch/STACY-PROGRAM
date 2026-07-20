#!/bin/bash
# Upload local shell history to STACY
# Usage: ./upload_history.sh <API_TOKEN> [API_URL]
#   API_URL defaults to https://stacyprogram.online
# El token tambien puede pasarse via variable de entorno STACY_TOKEN.

TOKEN="${STACY_TOKEN:-$1}"
API_URL="${2:-https://stacyprogram.online}"

if [ -z "$TOKEN" ]; then
    echo "Usage: $0 <API_TOKEN> [API_URL]"
    echo ""
    echo "1. Log in to STACY at https://stacyprogram.online"
    echo "2. Click 'Copy Token' button"
    echo "3. Run: STACY_TOKEN=<PEGA_TOKEN> bash $0"
    exit 1
fi

# Detect history file
if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zsh_history" ]; then
    HISTORY_FILE="$HOME/.zsh_history"
elif [ -f "$HOME/.bash_history" ]; then
    HISTORY_FILE="$HOME/.bash_history"
else
    echo "No se encontro .bash_history ni .zsh_history"
    exit 1
fi

MAQUINA=$(hostname)
echo "Maquina detectada: $MAQUINA"
echo "Leyendo historial desde: $HISTORY_FILE"

# Los valores se pasan por ENTORNO y se leen con os.environ dentro de Python:
# ningun dato del usuario se interpola en el codigo fuente => no hay inyeccion de comandos.
COMMANDS=$(
  STACY_HISTORY_FILE="$HISTORY_FILE" STACY_MAQUINA="$MAQUINA" python3 - <<'PY'
import json, os, sys
path = os.path.expanduser(os.environ['STACY_HISTORY_FILE'])
maquina = os.environ['STACY_MAQUINA']
if not os.path.exists(path):
    sys.exit(1)

comandos = []
seen = set()
with open(path, errors='ignore') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
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
PY
)

if [ -z "$COMMANDS" ]; then
    echo "Error al leer el historial"
    exit 1
fi

COUNT=$(printf '%s' "$COMMANDS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)['comandos']))")
echo "Enviando $COUNT comandos a $API_URL/comandos/importar ..."

RESPONSE=$(curl -s -X POST "$API_URL/comandos/importar" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$COMMANDS")

echo "Respuesta: $RESPONSE"
