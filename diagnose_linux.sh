#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "== SATURN Linux diagnostics =="
echo "System        : $(uname -a)"
echo "Session type  : ${XDG_SESSION_TYPE:-unknown}"
echo "Desktop       : ${XDG_CURRENT_DESKTOP:-${DESKTOP_SESSION:-unknown}}"
echo "DISPLAY       : ${DISPLAY:-not set}"
echo "WAYLAND       : ${WAYLAND_DISPLAY:-not set}"
echo

echo "== Commands =="
for cmd in python3 xdg-open playerctl pactl gnome-screenshot flameshot spectacle flatpak obs obs-studio code codium discord spotify steam telegram-desktop; do
  if command -v "$cmd" >/dev/null 2>&1; then
    printf "%-18s OK  %s\n" "$cmd" "$(command -v "$cmd")"
  else
    printf "%-18s --\n" "$cmd"
  fi
done
echo

echo "== Python packages =="
python3 - <<'PY'
packages = ["flask", "flask_socketio", "keyboard", "pynput", "pyautogui", "obsws_python"]
for package in packages:
    try:
        __import__(package)
        print(f"{package:<18} OK")
    except Exception as exc:
        print(f"{package:<18} --  {exc}")
PY
