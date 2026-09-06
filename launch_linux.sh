#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
clear
printf '\n==========================================\n'
printf '        SATURN Control v1.1\n'
printf '        FD Labs · Linux Edition\n'
printf '==========================================\n\n'
printf '[1/5] Revisando Python...\n'
if ! command -v python3 >/dev/null 2>&1; then
  echo '[ERROR] No encontre python3. Instalalo y volve a correr.'
  exit 1
fi
printf '[2/5] Preparando entorno virtual...\n'
python3 -m venv .venv
printf '[3/5] Actualizando pip...\n'
.venv/bin/python -m pip install --upgrade pip >/dev/null
printf '[4/5] Instalando/validando dependencias Python...\n'
.venv/bin/python -m pip install -r requirements-linux.txt
printf '\n[5/5] Iniciando SATURN...\n'
printf 'Panel: http://127.0.0.1:5000\n'
printf 'Para cerrar: Ctrl+C\n\n'
.venv/bin/python app.py
