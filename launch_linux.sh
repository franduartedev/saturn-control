#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

clear
echo
echo "=========================================="
echo "           SATURN Stream Deck"
echo "=========================================="
echo
echo "Iniciando el panel de macros..."
echo "No cierres esta ventana mientras uses SATURN."
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "[SATURN] Python 3 no está instalado."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Preparando entorno por primera vez..."
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "Revisando dependencias..."
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

clear
echo
echo "=========================================="
echo "             SATURN está listo"
echo "=========================================="
echo
echo "Panel web: http://localhost:5000"
echo
echo "Se abrirá en tu navegador automáticamente."
echo "Para cerrar SATURN, volvé a esta ventana y presioná CTRL+C."
echo
python app.py
