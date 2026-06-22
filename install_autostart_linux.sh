#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/saturn-streamdeck.desktop"

mkdir -p "$AUTOSTART_DIR"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=SATURN Stream Deck
Comment=Macro pad controller
Exec=$APP_DIR/launch_linux.sh
Path=$APP_DIR
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

echo "[SATURN] Autoinicio instalado:"
echo "$DESKTOP_FILE"
