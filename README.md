# SATURN Control v1.1

**SATURN Control** es el panel local de FD Labs para controlar un macro deck casero basado en Arduino Pro Micro / Leonardo.

Esta versión está pensada para Linux/X11 y fue probada con el flujo:

- Pro Micro detectado como `Arduino Leonardo (CDC ACM, HID)`
- Firmware enviando `F13` a `F18`
- SATURN mapeando los 6 botones
- Multimedia controlada con `playerctl`
- Volumen controlado con `wpctl` / `pactl`

## Instalación rápida en Arch / EndeavourOS / XFCE

```bash
sudo pacman -S --needed python python-pip tk playerctl wireplumber xdotool xdg-utils evtest usbutils
cd saturn_control_v1_1_linux_professional
chmod +x *.sh
./diagnose_linux.sh
./launch_linux.sh
```

Después abrí:

```text
http://127.0.0.1:5000
```

## Test de hardware

```bash
sudo evtest
```

Elegí el dispositivo `Arduino Leonardo` y apretá los botones. Lo esperado:

```text
Botón 1 -> KEY_F13
Botón 2 -> KEY_F14
Botón 3 -> KEY_F15
Botón 4 -> KEY_F16
Botón 5 -> KEY_F17
Botón 6 -> KEY_F18
```

## Qué trae v1.1

- UI más armada y profesional.
- Editor de macros desde la web.
- Selector y gestor básico de perfiles.
- Catálogo de acciones con parámetros.
- Diagnóstico de listener, sesión, dependencias y último botón.
- Eventos en tiempo real.
- Soporte para keysyms raros de X11/XFCE (`<269025...>`).
- Perfil FD Labs preparado para abrir herramientas propias.
- Script para crear acceso en menú de Linux.

## Acciones soportadas

- Multimedia: play/pause, anterior, siguiente.
- Audio: volumen +, volumen -, mute, mute mic.
- Apps: navegador, OBS, VS Code/Codium, Discord, Spotify, Telegram, terminal.
- Sistema: capturas, abrir carpeta, atajos con `xdotool`, escribir texto.
- Web: abrir URL.
- OBS: escenas, grabar, stream y mute por WebSocket si OBS WebSocket está configurado.

## Acceso en menú de Linux

```bash
./install_desktop_linux.sh
```

Esto crea un acceso `SATURN Control` en el menú de aplicaciones.

## Próximos pasos

- SATURN v1.1 estable en GitHub.
- Keycaps impresas para el deck de 6 botones.
- SATURN v2: 4 botones + 2 potenciómetros + OLED.
- Integración con ATLAS.
