# Changelog

## 1.1.1 - 2026-09-06

Fusión v1 (Windows) + edición Linux profesional. Misma base multiplataforma.

### Agregado / arreglado

- Soporte Windows mantenido: pycaw, pyautogui, rutas APPDATA, `run_saturn_server` para `desktop_app.py`.
- Linux real: `playerctl` (fallback xdotool), `wpctl` → `pactl`, `xdg-open`, flatpak, `xdotool` para hotkeys/type.
- Diagnóstico F13-F18: evdev 183-188, keysyms X11/XFCE, HID 0x68-0x6D + raw visible + `tools/key_watch_pynput.py`.
- Perfiles/autoguardado: crear/duplicar/renombrar/eliminar/cambiar persiste; autoguardado debounce 1.5s + indicador.
- Selector de acciones custom con buscador/filtro; catálogo unificado (incluye dev, system, open_app, system_command).
- `diagnose_linux.sh` extendido, `requirements-linux.txt` + `requirements.txt` unificados.
- README multiplataforma y versión 1.1.1 en app, web y scripts.

## 1.0.0 - 2026-06-23

Primera versión estable de SATURN Control.

### Agregado

- Panel de control visual para macro deck casero.
- UI local estilo SATURN/FD Labs con modo app de escritorio.
- Soporte para Arduino Pro Micro como teclado HID.
- Firmware para 6 botones físicos usando `F13` a `F18`.
- Diagnóstico de teclas detectadas.
- Configuración de macros desde la interfaz web.
- Perfiles de macros.
- Acciones para multimedia, sistema, apps, web, OBS, VS Code y comandos personalizados.
- Build Windows con PyInstaller.
- Instalador Windows con Inno Setup.
- Icono personalizable desde imagen.
- Scripts Linux para ejecución y autoinicio.

### Notas

- La configuración del usuario en Windows se guarda en `%APPDATA%\SATURN Control\config.json`.
- El instalador final se genera en `release\SATURN-Control-Setup-1.0.0.exe`.
