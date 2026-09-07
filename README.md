# SATURN Control v1.1.1

**SATURN Control** es el panel local de FD Labs para controlar un macro deck casero basado en Arduino Pro Micro / Leonardo (6 botones → `F13`–`F18`).

v1.1.1 fusiona la **v1 Windows** con la **edición Linux profesional**: mismo `app.py`, misma web, ambos SO soportados.

## Qué trae v1.1.1

- Windows mantenido: `launch_desktop.bat`, `.exe` con PyInstaller/Inno Setup, `pycaw` para mic, `pyautogui` para hotkeys, config en `%APPDATA%\SATURN Control`.
- Linux real: multimedia con `playerctl` (fallback `xdotool`), volumen/mute con `wpctl` → `pactl`, apps con `xdg-open`/binarios/flatpak, hotkeys y type-text con `xdotool`.
- Diagnóstico F13–F18: normaliza `pynput`/`keyboard`, evdev `183–188`, keysyms X11/XFCE (`269025093…`), HID `0x68–0x6D`. Vista Diagnóstico con última tecla, raw, botón, backend, sesión y dependencias.
- Perfiles + autoguardado: crear/duplicar/renombrar/eliminar/cambiar perfil persiste vía `POST /api/config`; edición de botones con autoguardado debounce 1.5s + botón Guardar con indicador `*`.
- Selector de acciones custom con buscador/filtro por nombre, id, categoría y descripción; catálogo unificado (Multimedia, Audio, Apps, Sistema, Web, Custom, Avanzado, Dev, OBS).
- `desktop_app.py` reparado (`run_saturn_server`), `tools/key_watch_pynput.py` con normalización, `diagnose_linux.sh` extendido.

## Windows (desarrollo / uso)

```bat
launch_desktop.bat
```

Instalador:

```bat
build_release_winteros.bat
```

Sale en `release\SATURN-Control-Setup-1.1.1.exe`. Config de usuario en `%APPDATA%\SATURN Control\config.json`.

## Linux (Arch / EndeavourOS / XFCE)

```bash
sudo pacman -S --needed python python-pip tk playerctl wireplumber xdotool xdg-utils evtest usbutils
chmod +x *.sh
./diagnose_linux.sh
./launch_linux.sh
```

Panel: `http://127.0.0.1:5000`. Detalle en `README_LINUX.md`.

## Test de hardware

```bash
sudo evtest
# o
.venv/bin/python tools/key_watch_pynput.py
```

Esperado:

```text
Botón 1 -> KEY_F13 / f13
Botón 2 -> KEY_F14 / f14
Botón 3 -> KEY_F15 / f15
Botón 4 -> KEY_F16 / f16
Botón 5 -> KEY_F17 / f17
Botón 6 -> KEY_F18 / f18
```

Si multimedia/volumen falla:

```bash
playerctl play-pause
wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+
pactl info | head -5
```

Diagnóstico vivo: `curl -s http://127.0.0.1:5000/api/diagnostics | python3 -m json.tool | head -80`

## Acciones soportadas

Multimedia/Audio (`play_pause`, `prev/next_track`, `volume_up/down`, `mute`, `mute_mic`), Apps (navegador, OBS, VS Code/Codium, Discord, Spotify, Steam, Telegram, Obsidian, terminal), Sistema (home, carpeta, app/ruta, captura, show_desktop, lock, sleep, monitor), Web (`custom_url`, YouTube, Twitch), Custom (`custom_hotkey`, `type_text`), Avanzado (`run_command`, `system_command`), Dev (`vscode_*`), OBS por WebSocket.

## Menú Linux

```bash
./install_desktop_linux.sh
```

## Roadmap

- v1.1.1 estable multiplataforma.
- Keycaps impresas 6 botones.
- v2: 4 botones + 2 potenciómetros + OLED + ATLAS.
