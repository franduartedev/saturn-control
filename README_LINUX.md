# SATURN Stream Deck V2 en Linux

## Probado para

- Linux Mint / Ubuntu / Debian.
- Sesion grafica X11 recomendada.
- Wayland puede bloquear atajos globales en algunas distros.

## Que trae esta V2

- Deteccion de sistema operativo.
- Diagnostico en `http://localhost:5000/api/diagnostics`.
- Panel web para configurar macros sin editar JSON a mano.
- Seccion "Como usar" dentro de la web.
- Comandos configurables por sistema operativo desde `config.json`.
- Launcher Linux con entorno virtual.
- Instalador de autoinicio Linux.

## Instalar dependencias del sistema

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-tk xclip scrot xdotool pulseaudio-utils playerctl
```

## Ejecutar

```bash
chmod +x launch_linux.sh
./launch_linux.sh
```

Despues abre:

```text
http://localhost:5000
```

## Configurar macros desde la web

1. Entra a `http://localhost:5000`.
2. Elegi el perfil activo.
3. Selecciona un boton F13-F18.
4. Cambia el nombre visible, la accion y los parametros.
5. Usa `Probar` para ejecutar la macro.
6. Usa `Guardar cambios` para dejarla fija en `config.json`.

La seccion `Como usar` esta dentro del panel para usuarios que no conocen el sistema.

## Diagnosticar

```bash
chmod +x diagnose_linux.sh
./diagnose_linux.sh
```

Tambien podes ver el reporte JSON en:

```text
http://localhost:5000/api/diagnostics
```

## Activar autoinicio

```bash
chmod +x install_autostart_linux.sh uninstall_autostart_linux.sh
./install_autostart_linux.sh
```

Para sacarlo:

```bash
./uninstall_autostart_linux.sh
```

## Notas importantes

- El macropad debe enviar `F13`, `F14`, `F15`, `F16`, `F17` y `F18`, igual que en Windows.
- En Linux se intenta usar `pynput` como listener principal.
- Si no detecta teclas, revisa que estes usando X11. En la pantalla de login suele aparecer una opcion de sesion.
- Las acciones de media usan `playerctl`.
- Las acciones de volumen y `mute_mic` usan `pactl`, incluido en `pulseaudio-utils`.
- Apps como OBS, Discord, Spotify y Steam se abren si estan instaladas como comando normal o Flatpak.

## Atajos que dependen del escritorio

Algunos atajos como mostrar escritorio, snap left/right, historial del portapapeles o panel de notificaciones pueden variar entre Cinnamon, GNOME, KDE o XFCE. Las acciones base de media, volumen, abrir apps, OBS WebSocket, carpetas, URLs y comandos personalizados son las mas portables.

## Personalizar comandos por sistema

En `config.json`, la seccion `system_commands` permite cambiar comandos sin tocar Python. Ejemplo:

```json
"system_commands": {
  "linux": {
    "open_vscode": [["code"], ["codium"]],
    "open_obs": [["obs"], ["flatpak", "run", "com.obsproject.Studio"]]
  },
  "windows": {},
  "macos": {}
}
```

Tambien existe la accion `system_command` para botones personalizados:

```json
{
  "action": "system_command",
  "label": "Mi script",
  "params": {
    "linux": "./scripts/mi-script.sh",
    "windows": "powershell.exe -File scripts\\mi-script.ps1"
  }
}
```
