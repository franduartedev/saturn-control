#!/usr/bin/env bash
set -euo pipefail

DESKTOP_FILE="$HOME/.config/autostart/saturn-streamdeck.desktop"

if [ -f "$DESKTOP_FILE" ]; then
  rm "$DESKTOP_FILE"
  echo "[SATURN] Autoinicio eliminado."
else
  echo "[SATURN] No habia autoinicio instalado."
fi
