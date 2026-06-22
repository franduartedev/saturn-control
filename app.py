import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from collections import deque
from pathlib import Path

try:
    import pyautogui
    PYAUTOGUI_OK = True
except ImportError:
    pyautogui = None
    PYAUTOGUI_OK = False
    print("[SATURN] pyautogui no instalado — acciones de hotkeys no disponibles. Corré: pip install pyautogui")
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_socketio import SocketIO

try:
    import keyboard as keyboard_lib
    KEYBOARD_OK = True
except ImportError:
    keyboard_lib = None
    KEYBOARD_OK = False

try:
    from pynput import keyboard as pynput_keyboard
    PYNPUT_OK = True
except ImportError:
    pynput_keyboard = None
    PYNPUT_OK = False

SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == "windows"
IS_LINUX = SYSTEM == "linux"
IS_MACOS = SYSTEM == "darwin"
APP_VERSION = "1.0.0"
SYSTEM_KEY = "windows" if IS_WINDOWS else "linux" if IS_LINUX else "macos" if IS_MACOS else SYSTEM

if IS_WINDOWS:
    try:
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        PYCAW_OK = True
    except ImportError:
        PYCAW_OK = False
        print("[SATURN] pycaw no instalado — mute_mic no disponible. Corré: pip install pycaw comtypes")
else:
    PYCAW_OK = False

try:
    import obsws_python  # noqa: F401
    OBSWS_OK = True
except ImportError:
    OBSWS_OK = False
    print("[SATURN] obsws-python no instalado — acciones OBS no disponibles. Corré: pip install obsws-python")

def runtime_base_dir():
    if getattr(sys, "frozen", False):
        if IS_WINDOWS:
            return Path(os.environ.get("APPDATA", Path.home())) / "SATURN Control"
        if IS_MACOS:
            return Path.home() / "Library" / "Application Support" / "SATURN Control"
        return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "saturn-control"
    return Path(__file__).resolve().parent


def bundled_resource_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).resolve()
    return Path(__file__).resolve().parent


BASE_DIR = runtime_base_dir()
RESOURCE_DIR = bundled_resource_dir()
WEB_DIR = RESOURCE_DIR / "web"
CONFIG_PATH = BASE_DIR / "config.json"
DEFAULT_CONFIG_PATH = RESOURCE_DIR / "config.json"

app = Flask(__name__, static_folder=str(WEB_DIR))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
logging.getLogger("werkzeug").setLevel(logging.ERROR)

_config_cache = None
_config_lock  = threading.Lock()
_listener_handle = None
_events = deque(maxlen=120)
_key_events = deque(maxlen=40)
_runtime = {
    "listener": {
        "active": False,
        "backend": None,
        "error": None,
        "warning": None,
    },
    "last_key": None,
    "last_action": None,
}

WINDOWS_APP_PATHS = {
    "open_spotify": [
        r"C:\Users\{user}\AppData\Roaming\Spotify\Spotify.exe",
    ],
    "open_obs": [
        r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
        r"C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe",
        r"C:\Users\{user}\AppData\Local\obs-studio\bin\64bit\obs64.exe",
        r"C:\Program Files (x86)\Steam\steamapps\common\OBS Studio\bin\64bit\obs64.exe",
    ],
    "open_chrome": [
        r"C:\Users\{user}\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{user}\AppData\Local\Google\Chrome\Application\chrome.exe",
    ],
    "open_discord": [
        r"C:\Users\{user}\AppData\Local\Discord\app-*\Discord.exe",
    ],
    "open_vscode": [
        r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        r"C:\Program Files\Microsoft VS Code\Code.exe",
    ],
    "open_terminal": [
        r"C:\Users\{user}\AppData\Local\Microsoft\WindowsApps\wt.exe",
        r"C:\Program Files\PowerShell\7\pwsh.exe",
    ],
    "open_steam": [
        r"C:\Program Files (x86)\Steam\steam.exe",
        r"C:\Program Files\Steam\steam.exe",
    ],
    "open_telegram": [
        r"C:\Users\{user}\AppData\Roaming\Telegram Desktop\Telegram.exe",
    ],
}

LINUX_APP_COMMANDS = {
    "open_spotify": [
        ["spotify"],
        ["flatpak", "run", "com.spotify.Client"],
    ],
    "open_obs": [
        ["obs"],
        ["obs-studio"],
        ["flatpak", "run", "com.obsproject.Studio"],
    ],
    "open_chrome": [
        ["brave-browser"],
        ["google-chrome"],
        ["chromium"],
        ["chromium-browser"],
        ["firefox"],
    ],
    "open_discord": [
        ["discord"],
        ["flatpak", "run", "com.discordapp.Discord"],
    ],
    "open_vscode": [
        ["code"],
        ["codium"],
    ],
    "open_terminal": [
        ["x-terminal-emulator"],
        ["gnome-terminal"],
        ["konsole"],
        ["xfce4-terminal"],
        ["mate-terminal"],
        ["kitty"],
        ["alacritty"],
    ],
    "open_steam": [
        ["steam"],
        ["flatpak", "run", "com.valvesoftware.Steam"],
    ],
    "open_telegram": [
        ["telegram-desktop"],
        ["flatpak", "run", "org.telegram.desktop"],
    ],
}

MACOS_APP_NAMES = {
    "open_spotify": "Spotify",
    "open_obs": "OBS",
    "open_chrome": "Google Chrome",
    "open_discord": "Discord",
    "open_vscode": "Visual Studio Code",
    "open_terminal": "Terminal",
    "open_steam": "Steam",
    "open_telegram": "Telegram",
}

LINUX_COMMAND_CHECKS = {
    "open_url/open_folder": ["xdg-open"],
    "media": ["playerctl"],
    "audio": ["pactl"],
    "screenshot": ["gnome-screenshot", "flameshot", "spectacle"],
    "flatpak_apps": ["flatpak"],
}

ACTION_CATALOG = {
    "media": [
        {"id": "play_pause", "name": "Play / Pause", "description": "Reproduce o pausa música/video.", "params": []},
        {"id": "prev_track", "name": "Anterior", "description": "Vuelve al track anterior.", "params": []},
        {"id": "next_track", "name": "Siguiente", "description": "Salta al siguiente track.", "params": []},
        {"id": "volume_up", "name": "Volumen +", "description": "Sube el volumen del sistema.", "params": []},
        {"id": "volume_down", "name": "Volumen -", "description": "Baja el volumen del sistema.", "params": []},
        {"id": "mute", "name": "Silenciar salida", "description": "Activa/desactiva mute del audio.", "params": []},
        {"id": "mute_mic", "name": "Silenciar micrófono", "description": "Activa/desactiva mute del micrófono.", "params": []},
    ],
    "system": [
        {"id": "screenshot", "name": "Captura", "description": "Abre captura de pantalla.", "params": []},
        {"id": "show_desktop", "name": "Mostrar escritorio", "description": "Minimiza/expone el escritorio.", "params": []},
        {"id": "lock_screen", "name": "Bloquear pantalla", "description": "Bloquea la sesión actual.", "params": []},
        {"id": "sleep", "name": "Suspender", "description": "Suspende el equipo.", "params": []},
        {"id": "file_explorer", "name": "Archivos", "description": "Abre la carpeta personal.", "params": []},
        {"id": "task_manager", "name": "Monitor del sistema", "description": "Abre administrador de tareas o monitor.", "params": []},
        {"id": "clipboard_history", "name": "Portapapeles", "description": "Abre historial del portapapeles si el escritorio lo soporta.", "params": []},
        {"id": "emoji_picker", "name": "Emojis", "description": "Abre selector de emojis si el escritorio lo soporta.", "params": []},
    ],
    "apps": [
        {"id": "open_spotify", "name": "Spotify", "description": "Abre Spotify.", "params": []},
        {"id": "open_obs", "name": "OBS", "description": "Abre OBS Studio.", "params": []},
        {"id": "open_chrome", "name": "Navegador", "description": "Abre Brave, Chrome, Chromium o Firefox.", "params": []},
        {"id": "open_discord", "name": "Discord", "description": "Abre Discord.", "params": []},
        {"id": "open_vscode", "name": "VS Code", "description": "Abre VS Code o Codium.", "params": []},
        {"id": "open_steam", "name": "Steam", "description": "Abre Steam.", "params": []},
        {"id": "open_telegram", "name": "Telegram", "description": "Abre Telegram Desktop.", "params": []},
        {"id": "open_terminal", "name": "Terminal", "description": "Abre una terminal.", "params": []},
    ],
    "web": [
        {"id": "open_youtube", "name": "YouTube", "description": "Abre YouTube.", "params": []},
        {"id": "open_twitch", "name": "Twitch", "description": "Abre Twitch.", "params": []},
        {"id": "custom_url", "name": "URL personalizada", "description": "Abre una URL indicada por el usuario.", "params": [{"name": "url", "label": "URL", "type": "url", "placeholder": "https://example.com"}]},
    ],
    "obs": [
        {"id": "obs_scene", "name": "Cambiar escena", "description": "Cambia la escena activa de OBS.", "params": [{"name": "scene", "label": "Nombre de escena", "type": "text", "placeholder": "Juegos"}]},
        {"id": "obs_start_stream", "name": "Iniciar stream", "description": "Inicia transmisión en OBS.", "params": []},
        {"id": "obs_stop_stream", "name": "Detener stream", "description": "Detiene transmisión en OBS.", "params": []},
        {"id": "obs_start_record", "name": "Iniciar grabación", "description": "Inicia grabación en OBS.", "params": []},
        {"id": "obs_stop_record", "name": "Detener grabación", "description": "Detiene grabación en OBS.", "params": []},
        {"id": "obs_toggle_mute_mic", "name": "Silenciar input OBS", "description": "Alterna mute de una fuente de audio de OBS.", "params": [{"name": "input", "label": "Input OBS", "type": "text", "placeholder": "Mic/Aux"}]},
    ],
    "dev": [
        {"id": "vscode_run", "name": "VS Code ejecutar", "description": "Ejecuta sin depuración.", "params": []},
        {"id": "vscode_build", "name": "VS Code compilar", "description": "Ejecuta build task.", "params": []},
        {"id": "vscode_debug", "name": "VS Code depurar", "description": "Inicia depuración.", "params": []},
        {"id": "vscode_stop", "name": "VS Code detener", "description": "Detiene depuración.", "params": []},
        {"id": "vscode_terminal", "name": "Terminal integrada", "description": "Abre/cierra terminal integrada.", "params": []},
        {"id": "vscode_format", "name": "Formatear", "description": "Formatea el archivo activo.", "params": []},
        {"id": "vscode_palette", "name": "Paleta de comandos", "description": "Abre la paleta de comandos.", "params": []},
        {"id": "vscode_save_all", "name": "Guardar todo", "description": "Guarda todos los archivos.", "params": []},
        {"id": "vscode_live_server_open", "name": "Live Server iniciar", "description": "Lanza Live Server desde VS Code.", "params": []},
        {"id": "vscode_live_server_stop", "name": "Live Server detener", "description": "Detiene Live Server desde VS Code.", "params": []},
    ],
    "custom": [
        {"id": "custom_hotkey", "name": "Atajo personalizado", "description": "Envia una combinacion de teclas.", "params": [{"name": "hotkey", "label": "Atajo", "type": "text", "placeholder": "ctrl+shift+p"}]},
        {"id": "type_text", "name": "Escribir texto", "description": "Escribe texto en la ventana activa.", "params": [{"name": "text", "label": "Texto", "type": "textarea", "placeholder": "Texto a escribir"}]},
        {"id": "open_app", "name": "Abrir app/ruta", "description": "Abre una app, archivo o comando.", "params": [{"name": "path", "label": "Ruta o comando", "type": "text", "placeholder": "/usr/bin/code"}]},
        {"id": "open_folder", "name": "Abrir carpeta", "description": "Abre una carpeta específica.", "params": [{"name": "path", "label": "Carpeta", "type": "text", "placeholder": "~/Proyectos"}]},
        {"id": "run_command", "name": "Comando shell", "description": "Ejecuta un comando de shell.", "params": [{"name": "command", "label": "Comando", "type": "text", "placeholder": "echo hola"}, {"name": "cwd", "label": "Carpeta de trabajo", "type": "text", "placeholder": "/home/fran"}]},
        {"id": "system_command", "name": "Comando por OS", "description": "Ejecuta comandos distintos segun el sistema.", "params": [{"name": "linux", "label": "Linux", "type": "text", "placeholder": "code"}, {"name": "windows", "label": "Windows", "type": "text", "placeholder": "notepad.exe"}, {"name": "macos", "label": "macOS", "type": "text", "placeholder": "open -a Safari"}]},
    ],
}


def log(message, level="info"):
    entry = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "message": message,
    }
    _events.append(entry)
    print(f"[SATURN] {message}")


def normalize_key_name(key_name):
    key = str(key_name or "").strip().lower()
    key = key.replace("key.", "")
    key = key.replace("keyboardkey.", "")
    key = key.replace("media_", "")
    key = key.replace(" ", "")
    if key.startswith("<") and key.endswith(">"):
        key = key[1:-1]
    if key.startswith("key_"):
        key = key[4:]
    if key.startswith("f") and key[1:].isdigit():
        return key
    aliases = {
        "esc": "escape",
        "return": "enter",
        "control": "ctrl",
        "control_l": "ctrl",
        "control_r": "ctrl",
        "shift_l": "shift",
        "shift_r": "shift",
        "alt_l": "alt",
        "alt_r": "alt",
        "cmd": "win",
        "cmd_l": "win",
        "cmd_r": "win",
        "windows": "win",
    }
    return aliases.get(key, key)


def build_button_key_map():
    buttons = get_active_buttons()
    key_map = {}
    for btn_id, button in buttons.items():
        configured_key = button.get("key") or f"F{12 + int(btn_id)}"
        normalized = normalize_key_name(configured_key)
        if normalized:
            key_map[normalized] = str(btn_id)
    return key_map


def record_key_event(raw_key, normalized_key, btn_id=None):
    event = {
        "raw": str(raw_key or ""),
        "key": str(normalized_key or "").upper(),
        "button": str(btn_id) if btn_id else None,
        "matched": bool(btn_id),
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _runtime["last_key"] = event
    _key_events.append(event)
    socketio.emit("key_event", event)


def load_config():
    global _config_cache
    with _config_lock:
        if _config_cache is None:
            ensure_config_file()
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                _config_cache = json.load(f)
        return _config_cache


def ensure_config_file():
    if CONFIG_PATH.exists():
        return
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DEFAULT_CONFIG_PATH.exists():
        shutil.copy2(DEFAULT_CONFIG_PATH, CONFIG_PATH)
        return
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"active_profile": "media", "profiles": {}}, f, indent=2)


def save_config(data):
    global _config_cache
    tmp = CONFIG_PATH.with_suffix(".tmp")
    with _config_lock:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.replace(CONFIG_PATH)
        _config_cache = data


def get_active_buttons():
    config = load_config()
    pid = config.get("active_profile", "media")
    return config["profiles"][pid]["buttons"]


def normalize_command(command):
    if isinstance(command, str):
        return command.split()
    if isinstance(command, list) and command:
        return [str(part) for part in command]
    return []


def configured_commands(action):
    config = load_config()
    commands = config.get("system_commands", {}).get(SYSTEM_KEY, {}).get(action, [])
    normalized = []
    for command in commands:
        cmd = normalize_command(command)
        if cmd:
            normalized.append(cmd)
    return normalized


def command_available(command):
    return bool(command and shutil.which(command[0]))


def session_info():
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "session_type": os.environ.get("XDG_SESSION_TYPE", ""),
        "desktop": os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION", ""),
        "display": os.environ.get("DISPLAY", ""),
        "wayland_display": os.environ.get("WAYLAND_DISPLAY", ""),
    }


def dependency_status():
    status = {
        "python_packages": {
            "keyboard": KEYBOARD_OK,
            "pynput": PYNPUT_OK,
            "pyautogui": PYAUTOGUI_OK,
            "obsws_python": OBSWS_OK,
            "pycaw": PYCAW_OK,
        },
        "commands": {},
    }
    if IS_LINUX:
        for group, commands in LINUX_COMMAND_CHECKS.items():
            status["commands"][group] = {
                command: bool(shutil.which(command))
                for command in commands
            }
        for action, commands in LINUX_APP_COMMANDS.items():
            status["commands"][action] = {
                "available": any(command_available(command) for command in commands),
                "candidates": [" ".join(command) for command in commands],
            }
    return status


def diagnostic_report():
    info = session_info()
    warnings = []
    if IS_LINUX and info["session_type"].lower() == "wayland":
        warnings.append("Wayland puede bloquear listeners globales; X11 suele ser mas estable para el macropad.")
    if IS_LINUX and not PYNPUT_OK:
        warnings.append("Falta pynput; el listener de teclado puede no arrancar.")
    if IS_LINUX and not shutil.which("pactl"):
        warnings.append("Falta pactl; volumen y mute_mic pueden fallar.")
    if IS_LINUX and not shutil.which("playerctl"):
        warnings.append("Falta playerctl; play/pause y cambio de cancion pueden fallar.")

    return {
        "app": {
            "name": "SATURN",
            "version": APP_VERSION,
            "config_path": str(CONFIG_PATH),
            "base_dir": str(BASE_DIR),
        },
        "system": info,
        "runtime": _runtime,
        "key_events": list(_key_events)[-20:],
        "dependencies": dependency_status(),
        "warnings": warnings,
        "events": list(_events)[-30:],
    }


def find_windows_executable(action):
    user = os.environ.get("USERNAME") or os.environ.get("USER", "")
    for tpl in WINDOWS_APP_PATHS.get(action, []):
        path = tpl.replace("{user}", user)
        if "*" in path:
            parent = Path(path).parent.parent
            name   = Path(path).name
            if parent.exists():
                matches = sorted(parent.glob(f"*/{name}"), reverse=True)
                if matches:
                    return str(matches[0])
        elif Path(path).exists():
            return path
    return None


def run_first_available(commands):
    for command in commands:
        exe = command[0]
        if shutil.which(exe):
            subprocess.Popen(command)
            log(f"Ejecutado: {' '.join(command)}")
            return True
    return False


def launch_named_app(action):
    custom_commands = configured_commands(action)
    if custom_commands and run_first_available(custom_commands):
        return True

    if IS_WINDOWS:
        exe = find_windows_executable(action)
        if exe:
            subprocess.Popen([exe], cwd=str(Path(exe).parent))
            log(f"Ejecutado: {exe}")
            return True
        return False

    if IS_LINUX:
        return run_first_available(LINUX_APP_COMMANDS.get(action, []))

    if IS_MACOS:
        app_name = MACOS_APP_NAMES.get(action)
        if app_name:
            subprocess.Popen(["open", "-a", app_name])
            return True
    return False


def open_url(url):
    webbrowser.open(url)


def open_path(path):
    path = str(Path(path).expanduser())
    if IS_WINDOWS:
        os.startfile(path)  # noqa: S606 - local user action launcher
    elif IS_MACOS:
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def press_hotkey(*keys):
    if not PYAUTOGUI_OK:
        log("pyautogui no instalado: no puedo enviar hotkeys.", "error")
        return
    pyautogui.hotkey(*keys)


def press_key(key):
    if not PYAUTOGUI_OK:
        log("pyautogui no instalado: no puedo enviar teclas.", "error")
        return
    pyautogui.press(key)


def type_text(text):
    if not text:
        return
    if KEYBOARD_OK:
        try:
            keyboard_lib.write(text)
            return
        except Exception as e:
            print(f"[SATURN] keyboard.write falló, uso pyautogui.write: {e}")
    if PYAUTOGUI_OK:
        pyautogui.write(text, interval=0.01)
    else:
        log("pyautogui no instalado: no puedo escribir texto.", "error")


def take_screenshot():
    if IS_WINDOWS:
        press_hotkey("win", "shift", "s")
        return
    if IS_LINUX and run_first_available([
        ["gnome-screenshot", "-a"],
        ["flameshot", "gui"],
        ["spectacle", "-r"],
    ]):
        return
    press_key("printscreen")


def handle_media_action(action):
    if IS_LINUX:
        playerctl_actions = {
            "play_pause": "play-pause",
            "next_track": "next",
            "prev_track": "previous",
        }
        if action in playerctl_actions and shutil.which("playerctl"):
            subprocess.Popen(["playerctl", playerctl_actions[action]])
            return
        if shutil.which("pactl"):
            if action == "volume_up":
                subprocess.Popen(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"])
                return
            if action == "volume_down":
                subprocess.Popen(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"])
                return
            if action == "mute":
                subprocess.Popen(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
                return

    key_names = {
        "play_pause": "playpause",
        "next_track": "nexttrack",
        "prev_track": "prevtrack",
        "volume_up": "volumeup",
        "volume_down": "volumedown",
        "mute": "volumemute",
    }
    press_key(key_names[action])


def lock_screen():
    if IS_WINDOWS:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    elif IS_LINUX:
        if not run_first_available([
            ["loginctl", "lock-session"],
            ["xdg-screensaver", "lock"],
            ["cinnamon-screensaver-command", "-l"],
            ["gnome-screensaver-command", "-l"],
        ]):
            print("[SATURN] No encontré comando para bloquear pantalla en Linux.")
    elif IS_MACOS:
        subprocess.run(["pmset", "displaysleepnow"])


def suspend_system():
    if IS_WINDOWS:
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"])
    elif IS_LINUX:
        subprocess.run(["systemctl", "suspend"])
    elif IS_MACOS:
        subprocess.run(["pmset", "sleepnow"])


def open_system_monitor():
    if IS_WINDOWS:
        subprocess.Popen(["taskmgr.exe"])
    elif IS_LINUX:
        if not run_first_available([
            ["gnome-system-monitor"],
            ["mate-system-monitor"],
            ["xfce4-taskmanager"],
            ["ksysguard"],
            ["systemmonitor"],
        ]):
            print("[SATURN] No encontré monitor de sistema en Linux.")
    elif IS_MACOS:
        subprocess.Popen(["open", "-a", "Activity Monitor"])


def open_settings():
    if IS_WINDOWS:
        press_hotkey("win", "i")
    elif IS_LINUX:
        if not run_first_available([
            ["cinnamon-settings"],
            ["gnome-control-center"],
            ["systemsettings"],
        ]):
            print("[SATURN] No encontré panel de configuración en Linux.")
    elif IS_MACOS:
        subprocess.Popen(["open", "-a", "System Settings"])


def toggle_mic_mute():
    if IS_WINDOWS and not PYCAW_OK:
        print("[SATURN] pycaw no instalado — corré: pip install pycaw comtypes")
        return
    if IS_LINUX:
        if not shutil.which("pactl"):
            print("[SATURN] pactl no instalado — instalá pulseaudio-utils para mute_mic en Linux.")
            return
        try:
            source = subprocess.check_output(["pactl", "get-default-source"], text=True).strip()
            subprocess.run(["pactl", "set-source-mute", source, "toggle"], check=True)
            print("[SATURN] Micrófono → toggle mute")
        except Exception as e:
            print(f"[SATURN] Error al silenciar micrófono en Linux: {e}")
        return
    if IS_MACOS:
        print("[SATURN] mute_mic todavía no está implementado en macOS.")
        return
    try:
        mic = AudioUtilities.GetMicrophone()
        if mic:
            interface = mic.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume    = cast(interface, POINTER(IAudioEndpointVolume))
            current   = volume.GetMute()
            volume.SetMute(not current, None)
            print(f"[SATURN] Micrófono → {'MUTED' if not current else 'UNMUTED'}")
    except Exception as e:
        print(f"[SATURN] Error al silenciar micrófono: {e}")


def obs_request(method, params=None):
    if not OBSWS_OK:
        print("[SATURN] obsws-python no instalado — corré: pip install obsws-python")
        return None
    try:
        import obsws_python as obs
        cfg      = load_config().get("obs", {})
        host     = cfg.get("host", "localhost")
        port     = cfg.get("port", 4455)
        password = cfg.get("password", "")
        cl = obs.ReqClient(host=host, port=port, password=password, timeout=3)
        fn = getattr(cl, method)
        result = fn(**params) if params else fn()
        cl.disconnect()
        return result
    except Exception as e:
        print(f"[SATURN] OBS WebSocket error ({method}): {e}")
        return None


def execute_system_command(params):
    commands = params.get(SYSTEM_KEY) or params.get("default") or params.get("command")
    if isinstance(commands, str):
        commands = [commands]
    if not commands:
        log(f"Sin comando para sistema '{SYSTEM_KEY}'", "warning")
        return

    for command in commands:
        cmd = normalize_command(command)
        if cmd and command_available(cmd):
            subprocess.Popen(cmd, cwd=params.get("cwd") or None)
            log(f"Comando OS ejecutado: {' '.join(cmd)}")
            return

    fallback = commands[0]
    fallback_shell = fallback if isinstance(fallback, str) else " ".join(normalize_command(fallback))
    subprocess.Popen(fallback_shell, shell=True, cwd=params.get("cwd") or None)
    log(f"Comando OS ejecutado con shell: {fallback_shell}")


def execute_action(action, params=None):
    params = params or {}
    try:
        _runtime["last_action"] = {
            "action": action,
            "params": params,
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        # ── Media ──────────────────────────────────────────────────────────
        if   action in ("play_pause", "next_track", "prev_track", "volume_up", "volume_down", "mute"):
            handle_media_action(action)
        elif action == "mute_mic":    toggle_mic_mute()

        # ── Sistema ─────────────────────────────────────────────────────────
        elif action == "screenshot":        take_screenshot()
        elif action == "show_desktop":      press_hotkey("win", "d")
        elif action == "lock_screen":       lock_screen()
        elif action == "sleep":             suspend_system()
        elif action == "file_explorer":     open_path(Path.home())
        elif action == "task_manager":      open_system_monitor()
        elif action == "clipboard_history": press_hotkey("win", "v")
        elif action == "emoji_picker":      press_hotkey("win", ".")
        elif action == "settings_panel":    open_settings()
        elif action == "notifications":     press_hotkey("win", "n")
        elif action == "maximize_window":   press_hotkey("win", "up")
        elif action == "snap_left":         press_hotkey("win", "left")
        elif action == "snap_right":        press_hotkey("win", "right")
        elif action == "close_window":      press_hotkey("alt", "f4")
        elif action == "task_view":         press_hotkey("win", "tab")
        elif action == "new_desktop":       press_hotkey("win", "ctrl", "d")

        # ── Web ─────────────────────────────────────────────────────────────
        elif action == "open_youtube": open_url("https://www.youtube.com")
        elif action == "open_twitch":  open_url("https://www.twitch.tv")
        elif action == "custom_url":
            url = params.get("url", "").strip()
            if url:
                open_url(url)

        # ── Dev (VS Code) ───────────────────────────────────────────────────
        elif action == "vscode_build":    press_hotkey("ctrl", "shift", "b")
        elif action == "vscode_run":      press_hotkey("ctrl", "f5")
        elif action == "vscode_debug":    press_key("f5")
        elif action == "vscode_stop":     press_hotkey("shift", "f5")
        elif action == "vscode_terminal": press_hotkey("ctrl", "`")
        elif action == "vscode_format":   press_hotkey("shift", "alt", "f")
        elif action == "vscode_palette":  press_hotkey("ctrl", "shift", "p")
        elif action == "vscode_save_all":
            press_hotkey("ctrl", "k")
            time.sleep(0.08)
            press_key("s")
        elif action == "vscode_live_server_open":
            press_hotkey("ctrl", "shift", "p")
            time.sleep(0.35)
            type_text("Live Server: Open with Live Server")
            time.sleep(0.2)
            press_key("enter")
        elif action == "vscode_live_server_stop":
            press_hotkey("ctrl", "shift", "p")
            time.sleep(0.35)
            type_text("Live Server: Stop Live Server")
            time.sleep(0.2)
            press_key("enter")

        # ── Apps ────────────────────────────────────────────────────────────
        elif action == "browser_devtools":   press_key("f12")
        elif action == "vscode_close_tab":   press_hotkey("ctrl", "w")
        elif action == "vscode_split":       press_hotkey("ctrl", "backslash")

        elif action in ("open_spotify", "open_obs", "open_chrome", "open_discord",
                        "open_vscode", "open_steam", "open_telegram", "open_terminal"):
            if not launch_named_app(action):
                print(f"[SATURN] No se encontró app/comando para '{action}' en {SYSTEM}.")

        elif action == "open_app":
            path = params.get("path", "").strip()
            if path and Path(path).exists():
                p = Path(path)
                if p.is_dir():
                    open_path(p)
                else:
                    subprocess.Popen([str(p)], cwd=str(p.parent))
            elif path:
                subprocess.Popen(path, shell=True)

        elif action == "open_folder":
            path = params.get("path", "").strip()
            if path:
                open_path(path)

        elif action == "run_command":
            cmd = params.get("command", "").strip()
            cwd = params.get("cwd", "").strip() or None
            if cmd:
                subprocess.Popen(cmd, shell=True, cwd=cwd)

        elif action == "system_command":
            execute_system_command(params)

        # ── OBS ─────────────────────────────────────────────────────────────
        elif action == "obs_scene":
            scene = params.get("scene", "").strip()
            if scene:
                obs_request("set_current_program_scene", {"scene_name": scene})
                print(f"[SATURN] OBS → Escena: {scene}")

        elif action == "obs_start_stream":
            obs_request("start_stream")
            print("[SATURN] OBS → Stream iniciado")

        elif action == "obs_stop_stream":
            obs_request("stop_stream")
            print("[SATURN] OBS → Stream detenido")

        elif action == "obs_start_record":
            obs_request("start_record")
            print("[SATURN] OBS → Grabación iniciada")

        elif action == "obs_stop_record":
            obs_request("stop_record")
            print("[SATURN] OBS → Grabación detenida")

        elif action == "obs_toggle_mute_mic":
            obs_request("toggle_input_mute", {"input_name": params.get("input", "Mic/Aux")})

        # ── Custom ──────────────────────────────────────────────────────────
        elif action == "custom_hotkey":
            hotkey = params.get("hotkey", "").strip()
            if hotkey:
                keys = [k.strip() for k in hotkey.lower().split("+")]
                press_hotkey(*keys)
        elif action == "type_text":
            text = params.get("text", "")
            if text:
                type_text(text)

    except Exception as e:
        print(f"[SATURN] Error en '{action}': {e}")
        socketio.emit("action_error", {"action": action, "error": str(e)})


def start_keyboard_listener():
    global _listener_handle
    last_fire = {}
    DEBOUNCE  = 0.12
    info = session_info()

    if IS_LINUX and info["session_type"].lower() == "wayland":
        _runtime["listener"]["warning"] = "Wayland detectado: los atajos globales pueden estar limitados."
        log(_runtime["listener"]["warning"], "warning")

    def trigger_key(key_name):
        key = normalize_key_name(key_name)
        key_map = build_button_key_map()
        if key not in key_map:
            record_key_event(key_name, key, None)
            return
        now = time.monotonic()
        if now - last_fire.get(key, 0) < DEBOUNCE:
            return
        last_fire[key] = now

        btn_id  = key_map[key]
        record_key_event(key_name, key, btn_id)
        buttons = get_active_buttons()
        btn_cfg = buttons.get(btn_id, {})
        action  = btn_cfg.get("action")
        params  = btn_cfg.get("params", {})
        if action:
            print(f"[SATURN] {key.upper()} → {action}")
            socketio.emit("button_press", {"id": int(btn_id)})
            threading.Thread(target=execute_action, args=(action, params), daemon=True).start()

    def start_pynput():
        def on_press(key):
            name = getattr(key, "name", None)
            if name is None:
                name = getattr(key, "char", None)
            trigger_key(name)

        listener = pynput_keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()
        _runtime["listener"].update({"active": True, "backend": "pynput", "error": None})
        log("Listener teclado: pynput")
        return listener

    if IS_LINUX and PYNPUT_OK:
        try:
            _listener_handle = start_pynput()
            return
        except Exception as e:
            _runtime["listener"].update({"active": False, "backend": "pynput", "error": str(e)})
            log(f"pynput no pudo iniciar: {e}", "error")

    if KEYBOARD_OK:
        try:
            keyboard_lib.on_press(lambda event: trigger_key(event.name))
            _runtime["listener"].update({"active": True, "backend": "keyboard", "error": None})
            log("Listener teclado: keyboard")
            return
        except Exception as e:
            _runtime["listener"].update({"active": False, "backend": "keyboard", "error": str(e)})
            log(f"keyboard no pudo iniciar: {e}", "error")

    if PYNPUT_OK:
        try:
            _listener_handle = start_pynput()
            return
        except Exception as e:
            _runtime["listener"].update({"active": False, "backend": "pynput", "error": str(e)})
            log(f"pynput no pudo iniciar: {e}", "error")

    _runtime["listener"].update({"active": False, "backend": None, "error": "No hay listener disponible"})
    log("No hay listener de teclado disponible. Instalá keyboard o pynput.", "error")


# ── API ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    web_index = WEB_DIR / "index.html"
    if not web_index.exists():
        html = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SATURN {APP_VERSION}</title>
  <style>
    body {{ margin: 0; font-family: system-ui, sans-serif; background: #07111f; color: #e7f0ff; }}
    main {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
    code, pre {{ background: #101d31; border: 1px solid #233b61; border-radius: 8px; }}
    pre {{ padding: 16px; overflow: auto; }}
    a {{ color: #7db7ff; }}
  </style>
</head>
<body>
  <main>
    <h1>SATURN {APP_VERSION}</h1>
    <p>Servidor activo. No encontre la carpeta <code>web/</code>, asi que muestro este panel minimo.</p>
    <p><a href="/api/diagnostics">Ver diagnostico JSON</a></p>
    <pre>URL: http://localhost:5000
Config: {CONFIG_PATH}</pre>
  </main>
</body>
</html>"""
        return Response(html, mimetype="text/html")
    return send_from_directory(str(WEB_DIR), "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(str(WEB_DIR), filename)

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(load_config())

@app.route("/api/diagnostics", methods=["GET"])
def get_diagnostics():
    return jsonify(diagnostic_report())

@app.route("/api/actions", methods=["GET"])
def get_actions():
    return jsonify(ACTION_CATALOG)

@app.route("/api/config", methods=["POST"])
def update_config():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Payload vacío"}), 400
    if "profiles" not in data or not isinstance(data["profiles"], dict):
        return jsonify({"error": "Falta profiles o no es valido"}), 400
    if "active_profile" not in data:
        data["active_profile"] = next(iter(data["profiles"]), "media")
    save_config(data)
    log("Configuracion guardada desde panel web")
    return jsonify({"ok": True})

@app.route("/api/obs/test", methods=["POST"])
def obs_test():
    if not OBSWS_OK:
        return jsonify({"ok": False, "error": "obsws-python no instalado"}), 200
    try:
        import obsws_python as obs
        data     = request.get_json() or {}
        host     = data.get("host", "localhost")
        port     = int(data.get("port", 4455))
        password = data.get("password", "")
        cl = obs.ReqClient(host=host, port=port, password=password, timeout=4)
        cl.get_version()
        cl.disconnect()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 200

@app.route("/api/test/<int:btn_id>", methods=["POST"])
def test_button(btn_id):
    buttons = get_active_buttons()
    btn_cfg = buttons.get(str(btn_id), {})
    action  = btn_cfg.get("action")
    params  = btn_cfg.get("params", {})
    if not action:
        return jsonify({"error": "Sin acción configurada"}), 404
    threading.Thread(target=execute_action, args=(action, params), daemon=True).start()
    return jsonify({"ok": True, "action": action})


def run_saturn_server(open_browser=True, host="127.0.0.1", port=5000):
    print("[SATURN] Panel iniciado correctamente.")
    print(f"[SATURN] Sistema: {platform.system()} {platform.release()}")
    if IS_LINUX:
        print(f"[SATURN] Sesion: {os.environ.get('XDG_SESSION_TYPE', 'desconocida')}")
    print(f"[SATURN] Configuracion: {CONFIG_PATH}")
    print(f"[SATURN] Web: http://localhost:{port}\n")

    start_keyboard_listener()
    if open_browser:
        threading.Timer(1.4, lambda: open_url(f"http://localhost:{port}")).start()
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_saturn_server(open_browser=True)
