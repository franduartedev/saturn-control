#!/usr/bin/env bash
cd "$(dirname "$0")"
echo '=========================================='
echo '        SATURN Linux Diagnóstico'
echo '=========================================='
echo
echo 'Sistema:'
echo "  Usuario   : $USER"
echo "  Sesión    : ${XDG_SESSION_TYPE:-desconocida}"
echo "  Escritorio: ${XDG_CURRENT_DESKTOP:-${DESKTOP_SESSION:-desconocido}}"
echo
echo 'USB / Pro Micro:'
if command -v lsusb >/dev/null 2>&1; then
  lsusb | grep -Ei 'arduino|leonardo|micro|sparkfun|2341|1b4f|32u4' || echo '  No vi Arduino/Pro Micro por nombre. Igual puede figurar genérico.'
else
  echo '  lsusb no instalado.'
fi
echo
echo 'Herramientas útiles:'
for c in python3 evtest playerctl pactl wpctl xdotool xdg-open; do
  if command -v "$c" >/dev/null 2>&1; then
    echo "  OK     $c -> $(command -v "$c")"
  else
    echo "  FALTA  $c"
  fi
done
echo
echo 'Comando recomendado en Arch/XFCE:'
echo '  sudo pacman -S --needed playerctl wireplumber xdotool xdg-utils evtest usbutils'
echo
echo 'Test de botones:'
echo '  sudo evtest'
echo 'Elegí Arduino Leonardo y apretá los botones. Deberías ver KEY_F13...KEY_F18.'
echo
