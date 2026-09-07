"""SATURN Control v1.1.1 — fusión v1 (Windows) + edición Linux profesional.

Mantiene Windows (pycaw/pyautogui/APP paths, APPDATA) y suma soporte Linux
real: playerctl/wpctl/pactl, xdotool, xdg-open, keysyms X11/XFCE y códigos
evdev/HID para F13-F18.
"""
import json
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from collections import deque
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

try:
    from flask_socketio import SocketIO
except Exception:
    SocketIO = None

try:
    import pyautogui
    PYAUTOGUI_OK = True
except ImportError:
    pyautogui = None
    PYAUTOGUI_OK = False

try:
    import keyboard as keyboard_lib
    KEYBOARD_OK = True
    KEYBOARD_ERROR = ""
except Exception as exc:
    keyboard_lib = None
    KEYBOARD_OK = False
    KEYBOARD_ERROR = str(exc)

try:
    from pynput import keyboard as pynput_keyboard
    PYNPUT_OK = True
    PYNPUT_ERROR = ""
except Exception as exc:
    pynput_keyboard = None
    PYNPUT_OK = False
    PYNPUT_ERROR = str(exc)

try:
    import obsws_python as obsws
    OBSWS_OK = True
    OBSWS_ERROR = ""
except Exception as exc:
    obsws = None
    OBSWS_OK = False
    OBSWS_ERROR = str(exc)

SYSTEM = platform.system().lower()
IS_WINDOWS = SYSTEM == "windows"
IS_LINUX = SYSTEM == "linux"
IS_MACOS = SYSTEM == "darwin"
SYSTEM_KEY = "windows" if IS_WINDOWS else "linux" if IS_LINUX else "macos" if IS_MACOS else SYSTEM

if IS_WINDOWS:
    try:
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        PYCAW_OK = True
    except ImportError:
        PYCAW_OK = False
else:
    PYCAW_OK = False

APP_NAME = "SATURN Control"
APP_VERSION = "1.1.1"


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
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading") if SocketIO else None
logging.getLogger("werkzeug").setLevel(logging.ERROR)

_config_cache = None
_config_lock = threading.Lock()
_listener_handle = None
_events = deque(maxlen=120)
_key_events = deque(maxlen=40)

runtime = {
    "app": APP_NAME,
    "version": APP_VERSION,
    "os": platform.system(),
    "platform": platform.platform(),
    "session": os.environ.get("XDG_SESSION_TYPE", "unknown"),
    "desktop": os.environ.get("XDG_CURRENT_DESKTOP", os.environ.get("DESKTOP_SESSION", "unknown")),
    "listener": {"active": False, "backend": "not-started", "error": None, "warning": None},
    "listener_backend": "not-started",
    "listener_ok": False,
    "listener_error": "",
    "last_key": None,
    "last_raw_key": None,
    "last_button": None,
    "last_action": None,
    "last_error": None,
    "started_at": time.strftime("%H:%M:%S"),
    "events": [],
}


def _emit(event, payload):
    if socketio:
        try:
            socketio.emit(event, payload)
        except Exception:
            pass


def add_event(kind, message, **extra):
    item = {"time": time.strftime("%H:%M:%S"), "kind": kind, "message": message, **extra}
    runtime["events"].insert(0, item)
    runtime["events"] = runtime["events"][:80]
    _events.append({"ts": item["time"], "level": kind, "message": message})
    print(f"[SATURN] {message}")
    _emit("saturn_event", item)
    return item


def log(message, level="info"):
    add_event(level, message)


def command_exists(name):
    return shutil.which(name) is not None


def run_command(args, *, shell=False, cwd=None, timeout=4):
    try:
        proc = subprocess.run(args, shell=shell, cwd=cwd, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        output = (proc.stdout or proc.stderr or "").strip()
        return proc.returncode == 0, output
    except Exception as exc:
        return False, str(exc)


def run_detached(args, *, shell=False, cwd=None):
    try:
        subprocess.Popen(args, shell=shell, cwd=cwd,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
        return True, "ok"
    except Exception as exc:
        return False, str(exc)


def first_existing_command(candidates):
    for cmd in candidates:
        exe = cmd[0] if isinstance(cmd, (list, tuple)) else str(cmd).split()[0]
        if command_exists(exe):
            return list(cmd) if isinstance(cmd, (list, tuple)) else cmd
    return None


def xdg_open(target):
    if IS_WINDOWS:
        try:
            os.startfile(target)  # noqa: S606 - user-triggered local launcher
            return True, "ok"
        except Exception as exc:
            return False, str(exc)
    if IS_MACOS:
        return run_detached(["open", target])
    if command_exists("xdg-open"):
        return run_detached(["xdg-open", target])
    return False, "xdg-open no está instalado"


# ── Config ────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "active_profile": "media",
    "settings": {"debounce_ms": 100, "open_browser_on_start": True, "theme": "saturn-dark"},
    "obs": {"host": "localhost", "password": "", "port": 4455},
    "profiles": {
        "media": {"name": "Media", "buttons": {
            "1": {"label": "Play / Pause", "key": "F13", "action": "play_pause", "params": {}},
            "2": {"label": "Anterior", "key": "F14", "action": "prev_track", "params": {}},
            "3": {"label": "Siguiente", "key": "F15", "action": "next_track", "params": {}},
            "4": {"label": "Silenciar", "key": "F16", "action": "mute", "params": {}},
            "5": {"label": "Volumen −", "key": "F17", "action": "volume_down", "params": {}},
            "6": {"label": "Volumen +", "key": "F18", "action": "volume_up", "params": {}}}},
        "stream": {"name": "Stream", "buttons": {
            "1": {"label": "Escena Juego", "key": "F13", "action": "obs_scene", "params": {"scene": "Juegos"}},
            "2": {"label": "Escena Cámara", "key": "F14", "action": "obs_scene", "params": {"scene": "Cámara"}},
            "3": {"label": "BRB", "key": "F15", "action": "obs_scene", "params": {"scene": "BRB"}},
            "4": {"label": "Mic", "key": "F16", "action": "mute_mic", "params": {}},
            "5": {"label": "Grabar", "key": "F17", "action": "obs_start_record", "params": {}},
            "6": {"label": "Detener", "key": "F18", "action": "obs_stop_record", "params": {}}}},
        "work": {"name": "Trabajo", "buttons": {
            "1": {"label": "VS Code", "key": "F13", "action": "open_vscode", "params": {}},
            "2": {"label": "Terminal", "key": "F14", "action": "open_terminal", "params": {}},
            "3": {"label": "Carpeta", "key": "F15", "action": "file_explorer", "params": {}},
            "4": {"label": "Navegador", "key": "F16", "action": "open_browser", "params": {}},
            "5": {"label": "Captura", "key": "F17", "action": "screenshot", "params": {}},
            "6": {"label": "GitHub", "key": "F18", "action": "custom_url", "params": {"url": "https://github.com"}}}},
        "fdlabs": {"name": "FD Labs", "buttons": {
            "1": {"label": "ATLAS", "key": "F13", "action": "open_folder", "params": {"path": str(Path.home())}},
            "2": {"label": "Obsidian", "key": "F14", "action": "open_obsidian", "params": {}},
            "3": {"label": "YouTube", "key": "F15", "action": "custom_url", "params": {"url": "https://www.youtube.com"}},
            "4": {"label": "GitHub", "key": "F16", "action": "custom_url", "params": {"url": "https://github.com"}},
            "5": {"label": "Terminal", "key": "F17", "action": "open_terminal", "params": {}},
            "6": {"label": "Música", "key": "F18", "action": "play_pause", "params": {}}}},
    },
}


def deep_merge(default, current):
    if isinstance(default, dict) and isinstance(current, dict):
        result = dict(default)
        for key, value in current.items():
            result[key] = deep_merge(result[key], value) if key in result else value
        return result
    return current


def ensure_config_file():
    if CONFIG_PATH.exists():
        return
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DEFAULT_CONFIG_PATH.exists() and DEFAULT_CONFIG_PATH != CONFIG_PATH:
        try:
            shutil.copy2(DEFAULT_CONFIG_PATH, CONFIG_PATH)
            return
        except Exception:
            pass
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)


def load_config():
    global _config_cache
    with _config_lock:
        if _config_cache is None:
            ensure_config_file()
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            _config_cache = deep_merge(DEFAULT_CONFIG, loaded)
            if _config_cache.get("active_profile") not in _config_cache.get("profiles", {}):
                _config_cache["active_profile"] = "media"
        return _config_cache


def save_config(data):
    global _config_cache
    if "profiles" not in data or not isinstance(data["profiles"], dict) or not data["profiles"]:
        raise ValueError("La configuración debe tener al menos un perfil")
    if data.get("active_profile") not in data.get("profiles", {}):
        data["active_profile"] = next(iter(data["profiles"].keys()))
    tmp = CONFIG_PATH.with_suffix(".tmp")
    with _config_lock:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.replace(CONFIG_PATH)
        _config_cache = data
    add_event("config", "Configuración guardada")


def active_profile_id():
    return load_config().get("active_profile", "media")


def active_profile():
    cfg = load_config()
    return cfg.get("profiles", {}).get(cfg.get("active_profile", "media"), {})


def get_active_buttons():
    return active_profile().get("buttons", {})


# ── Teclas F13-F18 ────────────────────────────────────────────────────────

EVDEV_CODES = {"183": "f13", "184": "f14", "185": "f15", "186": "f16", "187": "f17", "188": "f18"}
X11_KEYSYMS = {"269025153": "f13", "269025093": "f14", "269025094": "f15",
               "269025095": "f16", "269025096": "f17", "269025097": "f18"}
HID_CODES = {"70068": "f13", "70069": "f14", "7006a": "f15",
             "7006b": "f16", "7006c": "f17", "7006d": "f18"}


def normalize_key(value):
    """Normaliza nombres de teclas de pynput/keyboard/evdev/X11/HID a f13..f18."""
    if value is None:
        return ""
    s = str(value).strip().lower().replace("'", "").replace('"', "").replace(" ", "")
    s = s.strip("<>")
    s = s.replace("key.", "").replace("keyboardkey.", "").replace("key_", "").replace("key-", "")
    s = s.replace("media_", "")
    match = re.search(r"f(1[3-8])", s)
    if match:
        return f"f{match.group(1)}"
    if s in EVDEV_CODES:
        return EVDEV_CODES[s]
    if s in X11_KEYSYMS:
        return X11_KEYSYMS[s]
    if s in HID_CODES:
        return HID_CODES[s]
    aliases = {"esc": "escape", "return": "enter", "control": "ctrl",
               "control_l": "ctrl", "control_r": "ctrl", "shift_l": "shift",
               "shift_r": "shift", "alt_l": "alt", "alt_r": "alt",
               "cmd": "win", "cmd_l": "win", "cmd_r": "win", "windows": "win"}
    return aliases.get(s, s)


normalize_key_name = normalize_key


def button_map_from_config():
    mapping = {}
    for btn_id, btn in get_active_buttons().items():
        fallback = f"F{12 + int(btn_id)}" if str(btn_id).isdigit() else ""
        key = normalize_key((btn or {}).get("key") or fallback)
        if key:
            mapping[key] = str(btn_id)
    mapping.setdefault("f13", "1")
    mapping.setdefault("f14", "2")
    mapping.setdefault("f15", "3")
    mapping.setdefault("f16", "4")
    mapping.setdefault("f17", "5")
    mapping.setdefault("f18", "6")
    return mapping


build_button_key_map = button_map_from_config


def record_key_event(raw_key, normalized_key, btn_id=None):
    event = {"raw": str(raw_key or ""), "key": str(normalized_key or "").upper(),
             "button": str(btn_id) if btn_id else None, "matched": bool(btn_id),
             "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    runtime["last_key"] = event
    runtime["last_raw_key"] = event["raw"]
    if btn_id:
        runtime["last_button"] = str(btn_id)
    _key_events.append(event)
    _emit("key_event", event)


# ── Catálogo de acciones ──────────────────────────────────────────────────

ACTION_CATALOG = [
    {"id": "play_pause", "name": "Play / Pause", "category": "Multimedia", "icon": "play", "description": "Alterna reproducción (playerctl en Linux).", "fields": []},
    {"id": "next_track", "name": "Siguiente", "category": "Multimedia", "icon": "skip-forward", "description": "Pista/video siguiente.", "fields": []},
    {"id": "prev_track", "name": "Anterior", "category": "Multimedia", "icon": "skip-back", "description": "Pista/video anterior.", "fields": []},
    {"id": "volume_up", "name": "Subir volumen", "category": "Audio", "icon": "volume-2", "description": "Sube volumen (wpctl → pactl en Linux).", "fields": []},
    {"id": "volume_down", "name": "Bajar volumen", "category": "Audio", "icon": "volume-1", "description": "Baja volumen (wpctl → pactl en Linux).", "fields": []},
    {"id": "mute", "name": "Silenciar audio", "category": "Audio", "icon": "volume-x", "description": "Mute del sink principal.", "fields": []},
    {"id": "mute_mic", "name": "Silenciar micrófono", "category": "Audio", "icon": "mic-off", "description": "Mute del micrófono (pycaw en Windows).", "fields": []},
    {"id": "open_browser", "name": "Abrir navegador", "category": "Apps", "icon": "globe", "description": "Navegador predeterminado.", "fields": []},
    {"id": "open_chrome", "name": "Abrir Chrome/Chromium", "category": "Apps", "icon": "globe", "description": "Brave/Chrome/Chromium/Firefox.", "fields": []},
    {"id": "open_obs", "name": "Abrir OBS", "category": "Apps", "icon": "broadcast", "description": "Abre OBS Studio.", "fields": []},
    {"id": "open_vscode", "name": "Abrir VS Code", "category": "Apps", "icon": "code", "description": "VS Code / Codium.", "fields": []},
    {"id": "open_discord", "name": "Abrir Discord", "category": "Apps", "icon": "message", "description": "Abre Discord.", "fields": []},
    {"id": "open_spotify", "name": "Abrir Spotify", "category": "Apps", "icon": "music", "description": "Abre Spotify.", "fields": []},
    {"id": "open_steam", "name": "Abrir Steam", "category": "Apps", "icon": "gamepad", "description": "Abre Steam.", "fields": []},
    {"id": "open_telegram", "name": "Abrir Telegram", "category": "Apps", "icon": "send", "description": "Abre Telegram Desktop.", "fields": []},
    {"id": "open_obsidian", "name": "Abrir Obsidian", "category": "Apps", "icon": "book", "description": "Abre Obsidian.", "fields": []},
    {"id": "open_terminal", "name": "Abrir terminal", "category": "Sistema", "icon": "terminal", "description": "Terminal según tu SO/escritorio.", "fields": []},
    {"id": "file_explorer", "name": "Abrir home", "category": "Sistema", "icon": "folder", "description": "Abre tu carpeta personal.", "fields": []},
    {"id": "open_folder", "name": "Abrir carpeta", "category": "Sistema", "icon": "folder-open", "description": "Abre una carpeta específica.", "fields": [{"name": "path", "label": "Ruta", "type": "text", "placeholder": "/home/fran/Proyecto"}]},
    {"id": "open_app", "name": "Abrir app/ruta", "category": "Sistema", "icon": "package", "description": "Abre app, archivo o comando.", "fields": [{"name": "path", "label": "Ruta o comando", "type": "text", "placeholder": "/usr/bin/code"}]},
    {"id": "screenshot", "name": "Captura de pantalla", "category": "Sistema", "icon": "camera", "description": "Herramienta de captura disponible.", "fields": []},
    {"id": "show_desktop", "name": "Mostrar escritorio", "category": "Sistema", "icon": "layout", "description": "Minimiza/muestra escritorio (Win+D).", "fields": []},
    {"id": "lock_screen", "name": "Bloquear pantalla", "category": "Sistema", "icon": "lock", "description": "Bloquea la sesión.", "fields": []},
    {"id": "sleep", "name": "Suspender", "category": "Sistema", "icon": "moon", "description": "Suspende el equipo.", "fields": []},
    {"id": "task_manager", "name": "Monitor del sistema", "category": "Sistema", "icon": "activity", "description": "Taskmgr / monitor Linux.", "fields": []},
    {"id": "custom_url", "name": "Abrir URL", "category": "Web", "icon": "link", "description": "Abre una página web.", "fields": [{"name": "url", "label": "URL", "type": "url", "placeholder": "https://..."}]},
    {"id": "open_youtube", "name": "YouTube", "category": "Web", "icon": "play", "description": "Abre YouTube.", "fields": []},
    {"id": "open_twitch", "name": "Twitch", "category": "Web", "icon": "broadcast", "description": "Abre Twitch.", "fields": []},
    {"id": "custom_hotkey", "name": "Atajo de teclado", "category": "Custom", "icon": "keyboard", "description": "Envía combinación (xdotool en Linux).", "fields": [{"name": "hotkey", "label": "Atajo", "type": "text", "placeholder": "ctrl+shift+p"}]},
    {"id": "type_text", "name": "Escribir texto", "category": "Custom", "icon": "text", "description": "Escribe texto en ventana activa.", "fields": [{"name": "text", "label": "Texto", "type": "textarea", "placeholder": "Texto a escribir"}]},
    {"id": "run_command", "name": "Comando shell", "category": "Avanzado", "icon": "terminal-square", "description": "Ejecuta comando del sistema.", "fields": [{"name": "command", "label": "Comando", "type": "text", "placeholder": "echo hola"}, {"name": "cwd", "label": "Carpeta", "type": "text", "placeholder": "/home/fran"}]},
    {"id": "system_command", "name": "Comando por OS", "category": "Avanzado", "icon": "layers", "description": "Comandos distintos por SO.", "fields": [{"name": "linux", "label": "Linux", "type": "text", "placeholder": "code"}, {"name": "windows", "label": "Windows", "type": "text", "placeholder": "notepad.exe"}, {"name": "macos", "label": "macOS", "type": "text", "placeholder": "open -a Safari"}]},
    {"id": "vscode_run", "name": "VS Code: ejecutar", "category": "Dev", "icon": "play", "description": "Ctrl+F5.", "fields": []},
    {"id": "vscode_build", "name": "VS Code: compilar", "category": "Dev", "icon": "package", "description": "Ctrl+Shift+B.", "fields": []},
    {"id": "vscode_debug", "name": "VS Code: depurar", "category": "Dev", "icon": "bug", "description": "F5.", "fields": []},
    {"id": "vscode_terminal", "name": "VS Code: terminal", "category": "Dev", "icon": "terminal", "description": "Ctrl+` .", "fields": []},
    {"id": "vscode_palette", "name": "VS Code: paleta", "category": "Dev", "icon": "command", "description": "Ctrl+Shift+P.", "fields": []},
    {"id": "obs_scene", "name": "OBS: cambiar escena", "category": "OBS", "icon": "broadcast", "description": "Escena por WebSocket.", "fields": [{"name": "scene", "label": "Escena", "type": "text", "placeholder": "Juegos"}]},
    {"id": "obs_start_record", "name": "OBS: iniciar grabación", "category": "OBS", "icon": "record", "description": "Inicia grabación.", "fields": []},
    {"id": "obs_stop_record", "name": "OBS: detener grabación", "category": "OBS", "icon": "stop", "description": "Detiene grabación.", "fields": []},
    {"id": "obs_start_stream", "name": "OBS: iniciar stream", "category": "OBS", "icon": "radio", "description": "Inicia stream.", "fields": []},
    {"id": "obs_stop_stream", "name": "OBS: detener stream", "category": "OBS", "icon": "stop", "description": "Detiene stream.", "fields": []},
    {"id": "obs_toggle_mute_mic", "name": "OBS: mute input", "category": "OBS", "icon": "mic-off", "description": "Mute de fuente OBS.", "fields": [{"name": "input", "label": "Input", "type": "text", "placeholder": "Mic/Aux"}]},
]


def action_meta(action_id):
    return next((a for a in ACTION_CATALOG if a["id"] == action_id), None)


WINDOWS_APP_PATHS = {
    "open_spotify": [r"C:\Users\{user}\AppData\Roaming\Spotify\Spotify.exe"],
    "open_obs": [r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
                 r"C:\Program Files (x86)\obs-studio\bin\64bit\obs64.exe"],
    "open_chrome": [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"],
    "open_discord": [r"C:\Users\{user}\AppData\Local\Discord\Update.exe"],
    "open_vscode": [r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                    r"C:\Program Files\Microsoft VS Code\Code.exe"],
    "open_terminal": [r"C:\Users\{user}\AppData\Local\Microsoft\WindowsApps\wt.exe"],
    "open_steam": [r"C:\Program Files (x86)\Steam\steam.exe", r"C:\Program Files\Steam\steam.exe"],
    "open_telegram": [r"C:\Users\{user}\AppData\Roaming\Telegram Desktop\Telegram.exe"],
}

LINUX_APP_COMMANDS = {
    "open_spotify": [["spotify"], ["flatpak", "run", "com.spotify.Client"]],
    "open_obs": [["obs"], ["flatpak", "run", "com.obsproject.Studio"]],
    "open_chrome": [["brave-browser"], ["google-chrome"], ["chromium"], ["firefox"]],
    "open_browser": [["xdg-open", "https://www.google.com"]],
    "open_discord": [["discord"], ["flatpak", "run", "com.discordapp.Discord"]],
    "open_vscode": [["code"], ["codium"], ["flatpak", "run", "com.visualstudio.code"]],
    "open_obsidian": [["obsidian"], ["flatpak", "run", "md.obsidian.Obsidian"]],
    "open_terminal": [["xfce4-terminal"], ["x-terminal-emulator"], ["gnome-terminal"],
                      ["konsole"], ["alacritty"], ["kitty"]],
    "open_steam": [["steam"], ["flatpak", "run", "com.valvesoftware.Steam"]],
    "open_telegram": [["telegram-desktop"], ["flatpak", "run", "org.telegram.desktop"]],
}

MACOS_APP_NAMES = {"open_spotify": "Spotify", "open_obs": "OBS", "open_chrome": "Google Chrome",
                   "open_discord": "Discord", "open_vscode": "Visual Studio Code",
                   "open_terminal": "Terminal", "open_steam": "Steam", "open_telegram": "Telegram"}

LINUX_COMMAND_CHECKS = {
    "open_url/open_folder": ["xdg-open"], "media": ["playerctl"],
    "audio": ["wpctl", "pactl"], "hotkeys": ["xdotool"],
    "screenshot": ["gnome-screenshot", "flameshot", "spectacle"], "flatpak_apps": ["flatpak"],
}


def normalize_command(command):
    if isinstance(command, str):
        return command.split()
    if isinstance(command, list) and command:
        return [str(p) for p in command]
    return []


def configured_commands(action):
    try:
        commands = load_config().get("system_commands", {}).get(SYSTEM_KEY, {}).get(action, [])
    except Exception:
        commands = []
    return [c for c in (normalize_command(c) for c in commands) if c]


def command_available(command):
    return bool(command and shutil.which(command[0]))


def linux_media(action):
    if action == "play_pause":
        if command_exists("playerctl"):
            return run_command(["playerctl", "play-pause"], timeout=3)
        if command_exists("xdotool"):
            return run_command(["xdotool", "key", "XF86AudioPlay"], timeout=3)
        return False, "Falta playerctl o xdotool (sudo pacman -S playerctl xdotool)"
    if action == "next_track":
        if command_exists("playerctl"):
            return run_command(["playerctl", "next"], timeout=3)
        if command_exists("xdotool"):
            return run_command(["xdotool", "key", "XF86AudioNext"], timeout=3)
        return False, "Falta playerctl o xdotool"
    if action == "prev_track":
        if command_exists("playerctl"):
            return run_command(["playerctl", "previous"], timeout=3)
        if command_exists("xdotool"):
            return run_command(["xdotool", "key", "XF86AudioPrev"], timeout=3)
        return False, "Falta playerctl o xdotool"
    if action == "volume_up":
        if command_exists("wpctl"):
            return run_command(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%+"], timeout=3)
        if command_exists("pactl"):
            return run_command(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"], timeout=3)
        return False, "Falta wpctl o pactl (sudo pacman -S wireplumber pulseaudio)"
    if action == "volume_down":
        if command_exists("wpctl"):
            return run_command(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"], timeout=3)
        if command_exists("pactl"):
            return run_command(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"], timeout=3)
        return False, "Falta wpctl o pactl"
    if action == "mute":
        if command_exists("wpctl"):
            return run_command(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"], timeout=3)
        if command_exists("pactl"):
            return run_command(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"], timeout=3)
        return False, "Falta wpctl o pactl"
    if action == "mute_mic":
        if command_exists("wpctl"):
            return run_command(["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "toggle"], timeout=3)
        if command_exists("pactl"):
            try:
                source = subprocess.check_output(["pactl", "get-default-source"], text=True).strip()
                return run_command(["pactl", "set-source-mute", source, "toggle"], timeout=3)
            except Exception as exc:
                return False, str(exc)
        return False, "Falta wpctl o pactl"
    return False, "Acción multimedia desconocida"


def press_hotkey(*keys):
    if IS_LINUX and command_exists("xdotool") and not PYAUTOGUI_OK:
        combo = "+".join(keys)
        return run_command(["xdotool", "key", combo], timeout=3)
    if not PYAUTOGUI_OK:
        # Sin pyautogui en Linux intentamos xdotool directo
        if IS_LINUX and command_exists("xdotool"):
            return run_command(["xdotool", "key", "+".join(keys)], timeout=3)
        log("pyautogui no instalado: no puedo enviar hotkeys.", "error")
        return
    pyautogui.hotkey(*keys)


def press_key(key):
    if not PYAUTOGUI_OK:
        if IS_LINUX and command_exists("xdotool"):
            return run_command(["xdotool", "key", key], timeout=3)
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
        except Exception:
            pass
    if PYAUTOGUI_OK:
        try:
            pyautogui.write(text, interval=0.01)
            return
        except Exception:
            pass
    if IS_LINUX and command_exists("xdotool"):
        run_command(["xdotool", "type", "--clearmodifiers", text], timeout=5)
        return
    log("No puedo escribir texto: falta keyboard/pyautogui/xdotool.", "error")


def take_screenshot():
    if IS_WINDOWS:
        press_hotkey("win", "shift", "s")
        return
    if IS_LINUX and first_existing_command(
            [["xfce4-screenshooter"], ["gnome-screenshot", "-i"],
             ["flameshot", "gui"], ["spectacle"]]):
        cmd = first_existing_command(
            [["xfce4-screenshooter"], ["gnome-screenshot", "-i"],
             ["flameshot", "gui"], ["spectacle"]])
        run_detached(cmd)
        return
    press_key("printscreen")


def lock_screen():
    if IS_WINDOWS:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    elif IS_LINUX:
        if not run_first_available([["loginctl", "lock-session"], ["xdg-screensaver", "lock"],
                                    ["cinnamon-screensaver-command", "-l"],
                                    ["gnome-screensaver-command", "-l"]]):
            print("[SATURN] Sin comando de bloqueo en Linux.")
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
        if not run_first_available([["gnome-system-monitor"], ["mate-system-monitor"],
                                    ["xfce4-taskmanager"], ["ksysguard"]]):
            print("[SATURN] Sin monitor de sistema en Linux.")
    elif IS_MACOS:
        subprocess.Popen(["open", "-a", "Activity Monitor"])


def toggle_mic_mute():
    if IS_WINDOWS:
        if not PYCAW_OK:
            print("[SATURN] pycaw no instalado — pip install pycaw comtypes")
            return
        try:
            mic = AudioUtilities.GetMicrophone()
            if mic:
                interface = mic.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                current = volume.GetMute()
                volume.SetMute(not current, None)
        except Exception as exc:
            print(f"[SATURN] Error mute mic: {exc}")
        return
    if IS_LINUX:
        ok, detail = linux_media("mute_mic")
        if not ok:
            print(f"[SATURN] {detail}")
        return
    print("[SATURN] mute_mic no implementado en macOS.")


def find_windows_executable(action):
    user = os.environ.get("USERNAME") or os.environ.get("USER", "")
    for tpl in WINDOWS_APP_PATHS.get(action, []):
        path = tpl.replace("{user}", user)
        if "*" in path:
            parent = Path(path).parent.parent
            name = Path(path).name
            if parent.exists():
                matches = sorted(parent.glob(f"*/{name}"), reverse=True)
                if matches:
                    return str(matches[0])
        elif Path(path).exists():
            return path
    return None


def run_first_available(commands):
    for command in commands:
        if command and shutil.which(command[0]):
            subprocess.Popen(command)
            log(f"Ejecutado: {' '.join(command)}")
            return True
    return False


def launch_named_app(action):
    custom = configured_commands(action)
    if custom and run_first_available(custom):
        return True
    if IS_WINDOWS:
        exe = find_windows_executable(action)
        if exe:
            subprocess.Popen([exe], cwd=str(Path(exe).parent))
            log(f"Ejecutado: {exe}")
            return True
        # fallback: intentar comando directo (ej. code, spotify)
        linux_cmds = LINUX_APP_COMMANDS.get(action, [])
        for cmd in linux_cmds:
            if cmd and shutil.which(cmd[0]):
                subprocess.Popen(cmd)
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
        os.startfile(path)  # noqa: S606
    elif IS_MACOS:
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def obs_request(method, params=None):
    if not OBSWS_OK:
        return False, f"obsws-python no disponible: {OBSWS_ERROR}"
    try:
        cfg = load_config().get("obs", {})
        cl = obsws.ReqClient(host=cfg.get("host", "localhost"),
                             port=int(cfg.get("port", 4455)),
                             password=cfg.get("password", ""), timeout=3)
        fn = getattr(cl, method)
        result = fn(**(params or {})) if params else fn()
        try:
            cl.disconnect()
        except Exception:
            pass
        return True, str(result or "ok")
    except Exception as exc:
        return False, str(exc)


def execute_system_command(params):
    commands = params.get(SYSTEM_KEY) or params.get("default") or params.get("command")
    if isinstance(commands, str):
        commands = [commands]
    if not commands:
        log(f"Sin comando para '{SYSTEM_KEY}'", "warning")
        return
    for command in commands:
        cmd = normalize_command(command)
        if cmd and command_available(cmd):
            subprocess.Popen(cmd, cwd=params.get("cwd") or None)
            log(f"Comando OS ejecutado: {' '.join(cmd)}")
            return
    fallback = commands[0]
    shell_cmd = fallback if isinstance(fallback, str) else " ".join(normalize_command(fallback))
    subprocess.Popen(shell_cmd, shell=True, cwd=params.get("cwd") or None)
    log(f"Comando OS con shell: {shell_cmd}")


def execute_action(action, params=None):
    params = params or {}
    runtime["last_action"] = action
    meta = action_meta(action)
    action_name = meta["name"] if meta else action
    try:
        ok, detail = True, "ok"
        if action in {"play_pause", "next_track", "prev_track", "volume_up", "volume_down", "mute", "mute_mic"}:
            if IS_LINUX:
                ok, detail = linux_media(action)
            elif action == "mute_mic":
                toggle_mic_mute()
            else:
                press_key({"play_pause": "playpause", "next_track": "nexttrack",
                           "prev_track": "prevtrack", "volume_up": "volumeup",
                           "volume_down": "volumedown", "mute": "volumemute"}[action])
        elif action == "custom_url":
            url = params.get("url", "").strip()
            ok, detail = xdg_open(url) if url else (False, "URL vacía")
        elif action == "open_youtube":
            open_url("https://www.youtube.com")
        elif action == "open_twitch":
            open_url("https://www.twitch.tv")
        elif action in {"open_browser", "open_chrome"}:
            cmd = first_existing_command([["google-chrome"], ["chromium"], ["brave-browser"], ["firefox"]])
            if IS_WINDOWS and not cmd:
                ok = launch_named_app(action)
                detail = "" if ok else "No encontré navegador"
            else:
                ok, detail = run_detached(cmd) if cmd else xdg_open("https://www.google.com")
        elif action == "file_explorer":
            open_path(Path.home())
        elif action == "open_folder":
            open_path(params.get("path", "").strip() or str(Path.home()))
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
            else:
                ok, detail = False, "Ruta vacía"
        elif action in {"open_obs", "open_vscode", "open_discord", "open_spotify", "open_steam",
                        "open_telegram", "open_obsidian", "open_terminal"}:
            if not launch_named_app(action):
                ok, detail = False, f"No encontré app para '{action}' en {SYSTEM}"
        elif action == "screenshot":
            take_screenshot()
        elif action == "show_desktop":
            press_hotkey("win", "d")
        elif action == "lock_screen":
            lock_screen()
        elif action == "sleep":
            suspend_system()
        elif action == "task_manager":
            open_system_monitor()
        elif action in {"clipboard_history", "emoji_picker"}:
            press_hotkey("win", "v" if action == "clipboard_history" else ".")
        elif action == "run_command":
            cmd = params.get("command", "").strip()
            cwd = params.get("cwd", "").strip() or None
            ok, detail = run_detached(cmd, shell=True, cwd=cwd) if cmd else (False, "Comando vacío")
        elif action == "system_command":
            execute_system_command(params)
        elif action == "custom_hotkey":
            hotkey = params.get("hotkey", "").strip()
            if hotkey and IS_LINUX and command_exists("xdotool"):
                ok, detail = run_command(["xdotool", "key", hotkey], timeout=3)
            elif hotkey:
                press_hotkey(*[k.strip() for k in hotkey.lower().split("+")])
            else:
                ok, detail = False, "Atajo vacío"
        elif action == "type_text":
            text = params.get("text", "")
            if text:
                type_text(text)
            else:
                ok, detail = False, "Texto vacío"
        elif action in {"vscode_run", "vscode_build", "vscode_debug", "vscode_terminal",
                        "vscode_palette", "vscode_format"}:
            {"vscode_run": ("ctrl", "f5"), "vscode_build": ("ctrl", "shift", "b"),
             "vscode_debug": ("f5",), "vscode_terminal": ("ctrl", "`"),
             "vscode_palette": ("ctrl", "shift", "p"),
             "vscode_format": ("shift", "alt", "f")}.get(action)
            press_hotkey(*{"vscode_run": ("ctrl", "f5"), "vscode_build": ("ctrl", "shift", "b"),
                           "vscode_debug": ("f5",), "vscode_terminal": ("ctrl", "`"),
                           "vscode_palette": ("ctrl", "shift", "p"),
                           "vscode_format": ("shift", "alt", "f")}[action])
        elif action == "obs_scene":
            scene = params.get("scene", "").strip()
            ok, detail = obs_request("set_current_program_scene", {"scene_name": scene}) if scene else (False, "Escena vacía")
        elif action == "obs_start_record":
            ok, detail = obs_request("start_record")
        elif action == "obs_stop_record":
            ok, detail = obs_request("stop_record")
        elif action == "obs_start_stream":
            ok, detail = obs_request("start_stream")
        elif action == "obs_stop_stream":
            ok, detail = obs_request("stop_stream")
        elif action == "obs_toggle_mute_mic":
            ok, detail = obs_request("toggle_input_mute", {"input_name": params.get("input", "Mic/Aux")})
        else:
            ok, detail = False, f"Acción no implementada: {action}"
        if ok:
            runtime["last_error"] = None
            add_event("action", f"Ejecutado: {action_name}", action=action)
        else:
            runtime["last_error"] = detail
            add_event("warn", f"No se pudo ejecutar {action_name}: {detail}", action=action, error=detail)
    except Exception as exc:
        runtime["last_error"] = str(exc)
        add_event("error", f"Error en {action_name}: {exc}", action=action, error=str(exc))


def handle_key_name(key_name, raw=None):
    key = normalize_key(key_name)
    runtime["last_key"] = key.upper() if key else ""
    runtime["last_raw_key"] = str(raw if raw is not None else key_name)
    mapping = button_map_from_config()
    btn_id = mapping.get(key)
    record_key_event(raw if raw is not None else key_name, key, btn_id)
    if not btn_id:
        add_event("key", f"Tecla sin mapa: {key} (raw {runtime['last_raw_key']})", key=key)
        return
    runtime["last_button"] = btn_id
    btn_cfg = get_active_buttons().get(str(btn_id), {})
    action = btn_cfg.get("action")
    params = btn_cfg.get("params", {})
    label = btn_cfg.get("label", f"Botón {btn_id}")
    add_event("button", f"{key.upper()} → Botón {btn_id}: {label}", key=key, button=btn_id, action=action)
    _emit("button_press", {"id": int(btn_id)})
    if action:
        threading.Thread(target=execute_action, args=(action, params), daemon=True).start()


def _listener_trigger(key_name, last_fire, debounce):
    norm = normalize_key(key_name)
    now = time.monotonic()
    if now - last_fire.get(norm, 0) < debounce:
        return
    last_fire[norm] = now
    handle_key_name(norm, raw=key_name)


def start_pynput_listener():
    last_fire = {}
    debounce = max(20, int(load_config().get("settings", {}).get("debounce_ms", 100))) / 1000

    def on_press(key):
        raw = str(key)
        try:
            name = key.name
        except AttributeError:
            name = getattr(key, "char", None) or raw
        _listener_trigger(name, last_fire, debounce)

    listener = pynput_keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()
    runtime["listener_backend"] = "pynput"
    runtime["listener_ok"] = True
    runtime["listener"].update({"active": True, "backend": "pynput", "error": None})
    add_event("status", "Listener iniciado con pynput")


def start_keyboard_lib_listener():
    last_fire = {}
    debounce = max(20, int(load_config().get("settings", {}).get("debounce_ms", 100))) / 1000

    def on_key(event):
        if getattr(event, "event_type", "down") != "down":
            return
        _listener_trigger(event.name, last_fire, debounce)

    keyboard_lib.on_press(on_key)
    runtime["listener_backend"] = "keyboard"
    runtime["listener_ok"] = True
    runtime["listener"].update({"active": True, "backend": "keyboard", "error": None})
    add_event("status", "Listener iniciado con keyboard")


def start_keyboard_listener():
    global _listener_handle
    info_session = (os.environ.get("XDG_SESSION_TYPE", "") or "").lower()
    if IS_LINUX and info_session == "wayland":
        msg = "Wayland detectado: los atajos globales pueden estar limitados, X11 es más estable."
        runtime["listener"]["warning"] = msg
        log(msg, "warning")
    # En Linux priorizar pynput (mejor con F13-F18/X11), en Windows keyboard
    order = ["pynput", "keyboard"] if IS_LINUX else ["keyboard", "pynput"]
    for backend in order:
        if backend == "pynput" and PYNPUT_OK:
            try:
                start_pynput_listener()
                _listener_handle = True
                return
            except Exception as exc:
                runtime["listener_error"] = str(exc)
                log(f"pynput no pudo iniciar: {exc}", "error")
        if backend == "keyboard" and KEYBOARD_OK:
            try:
                start_keyboard_lib_listener()
                _listener_handle = True
                return
            except Exception as exc:
                runtime["listener_error"] = str(exc)
                log(f"keyboard no pudo iniciar: {exc}", "error")
    if not PYNPUT_OK:
        runtime["listener_error"] = PYNPUT_ERROR
    if not KEYBOARD_OK and not runtime["listener_error"]:
        runtime["listener_error"] = KEYBOARD_ERROR
    runtime["listener_backend"] = "none"
    runtime["listener_ok"] = False
    runtime["listener"].update({"active": False, "backend": None, "error": runtime["listener_error"] or "sin listener"})
    add_event("error", "Sin listener de teclado (instalá pynput/keyboard)")


def session_info():
    return {"system": platform.system(), "release": platform.release(),
            "version": platform.version(), "machine": platform.machine(),
            "python": platform.python_version(),
            "session_type": os.environ.get("XDG_SESSION_TYPE", ""),
            "desktop": os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION", ""),
            "display": os.environ.get("DISPLAY", ""),
            "wayland_display": os.environ.get("WAYLAND_DISPLAY", "")}


def system_dependencies():
    deps = {"python3": command_exists("python3"), "playerctl": command_exists("playerctl"),
            "pactl": command_exists("pactl"), "wpctl": command_exists("wpctl"),
            "xdotool": command_exists("xdotool"), "xdg-open": command_exists("xdg-open"),
            "evtest": command_exists("evtest"), "lsusb": command_exists("lsusb"),
            "pynput": PYNPUT_OK, "keyboard": KEYBOARD_OK,
            "pyautogui": PYAUTOGUI_OK, "pycaw": PYCAW_OK, "obsws-python": OBSWS_OK}
    return deps


def dependency_status():
    status = {"python_packages": {"keyboard": KEYBOARD_OK, "pynput": PYNPUT_OK,
                                  "pyautogui": PYAUTOGUI_OK, "obsws_python": OBSWS_OK,
                                  "pycaw": PYCAW_OK}, "commands": {}}
    if IS_LINUX:
        for group, commands in LINUX_COMMAND_CHECKS.items():
            status["commands"][group] = {c: bool(shutil.which(c)) for c in commands}
        for action, commands in LINUX_APP_COMMANDS.items():
            status["commands"][action] = {"available": any(command_available(c) for c in commands),
                                          "candidates": [" ".join(c) for c in commands]}
    return status


def diagnostic_report():
    info = session_info()
    warnings = []
    if IS_LINUX and info["session_type"].lower() == "wayland":
        warnings.append("Wayland puede bloquear listeners globales; X11 es más estable para el macropad.")
    if not PYNPUT_OK and not KEYBOARD_OK:
        warnings.append("Falta pynput/keyboard; el listener puede no arrancar.")
    if IS_LINUX and not command_exists("playerctl"):
        warnings.append("Falta playerctl; play/pause puede fallar (sudo pacman -S playerctl).")
    if IS_LINUX and not (command_exists("wpctl") or command_exists("pactl")):
        warnings.append("Falta wpctl/pactl; volumen y mute pueden fallar.")
    if IS_LINUX and not command_exists("xdotool"):
        warnings.append("Falta xdotool; hotkeys y type_text pueden fallar.")
    return {"app": {"name": runtime["app"], "version": APP_VERSION,
                    "config_path": str(CONFIG_PATH), "base_dir": str(BASE_DIR)},
            "system": info, "runtime": runtime,
            "key_events": list(_key_events)[-20:], "dependencies": dependency_status(),
            "warnings": warnings, "events": list(_events)[-30:]}


# ── API ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    web_index = WEB_DIR / "index.html"
    if not web_index.exists():
        html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>SATURN {APP_VERSION}</title></head><body>
<h1>SATURN {APP_VERSION}</h1><p>Servidor activo sin carpeta web/.</p>
<p><a href="/api/diagnostics">Diagnóstico JSON</a></p></body></html>"""
        return Response(html, mimetype="text/html")
    return send_from_directory(str(WEB_DIR), "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(str(WEB_DIR), filename)


@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(load_config())


@app.route("/api/config", methods=["POST"])
def update_config():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "payload vacío"}), 400
    try:
        save_config(data)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify({"ok": True})


@app.route("/api/actions")
def actions():
    return jsonify(ACTION_CATALOG)


@app.route("/api/diagnostics")
def diagnostics():
    report = diagnostic_report()
    return jsonify({**runtime, "dependencies": system_dependencies(),
                    "active_profile": active_profile_id(),
                    "key_map": button_map_from_config(),
                    "config_path": str(CONFIG_PATH), "web_dir": str(WEB_DIR),
                    "report": report, "warnings": report["warnings"],
                    "key_events": report["key_events"]})


@app.route("/api/events")
def events():
    return jsonify(runtime["events"])


@app.route("/api/test/<int:btn_id>", methods=["POST"])
def test_button(btn_id):
    btn_cfg = get_active_buttons().get(str(btn_id), {})
    action = btn_cfg.get("action")
    params = btn_cfg.get("params", {})
    if not action:
        return jsonify({"ok": False, "error": "sin acción"}), 404
    threading.Thread(target=execute_action, args=(action, params), daemon=True).start()
    return jsonify({"ok": True, "action": action})


@app.route("/api/obs/test", methods=["POST"])
def obs_test():
    data = request.get_json() or {}
    try:
        cfg = load_config()
        cfg["obs"] = {"host": data.get("host", cfg.get("obs", {}).get("host", "localhost")),
                      "port": int(data.get("port", cfg.get("obs", {}).get("port", 4455))),
                      "password": data.get("password", cfg.get("obs", {}).get("password", ""))}
        ok, detail = obs_request("get_version")
        return jsonify({"ok": ok, "message": detail})
    except Exception as exc:
        return jsonify({"ok": False, "message": str(exc)})


def open_browser_later(port=5000):
    if not load_config().get("settings", {}).get("open_browser_on_start", True):
        return
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{port}")


def run_saturn_server(open_browser=True, host="127.0.0.1", port=5000):
    """Entry point usado por desktop_app.py (pywebview) y por __main__."""
    print("[SATURN] Panel iniciado correctamente.")
    print(f"[SATURN] Sistema: {platform.system()} {platform.release()} ({SYSTEM_KEY})")
    if IS_LINUX:
        print(f"[SATURN] Sesión: {os.environ.get('XDG_SESSION_TYPE', 'desconocida')}")
    print(f"[SATURN] Configuración: {CONFIG_PATH}")
    print(f"[SATURN] Web: http://localhost:{port}\n")
    start_keyboard_listener()
    if open_browser:
        threading.Thread(target=open_browser_later, args=(port,), daemon=True).start()
    if socketio:
        socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
    else:
        app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    print("╔══════════════════════════════════════╗")
    print("║        SATURN Control v1.1.1         ║")
    print("║      FD Labs · Windows + Linux       ║")
    print("╚══════════════════════════════════════╝")
    print(f"Config : {CONFIG_PATH}")
    print("URL    : http://127.0.0.1:5000")
    print(f"Sesión : {runtime['session']} / {runtime['desktop']}\n")
    run_saturn_server(open_browser=True)
