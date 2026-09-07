#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
APP_DIR="$(pwd)"
DESKTOP_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$DESKTOP_DIR" "$AUTOSTART_DIR"
cat > "$DESKTOP_DIR/saturn-control.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=SATURN Control
Comment=FD Labs macro deck controller
Exec=$APP_DIR/launch_linux.sh
Path=$APP_DIR
Terminal=true
Categories=Utility;Development;
StartupNotify=false
EOF
chmod +x "$DESKTOP_DIR/saturn-control.desktop"
echo "Acceso instalado en el menú de aplicaciones: SATURN Control"
echo "Archivo: $DESKTOP_DIR/saturn-control.desktop"
echo
echo "Si querés autoinicio, corré:"
echo "  cp '$DESKTOP_DIR/saturn-control.desktop' '$AUTOSTART_DIR/saturn-control.desktop'"
