import json
import os
import platform
import re
import shutil
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

try:
    from flask_socketio import SocketIO
except Exception:
    SocketIO = None

try:
    from pynput import keyboard as pynput_keyboard
    PYNPUT_OK = True
    PYNPUT_ERROR = ""
except Exception as exc:
    pynput_keyboard = None
    PYNPUT_OK = False
    PYNPUT_ERROR = str(exc)

try:
    import keyboard as keyboard_lib
    KEYBOARD_OK = True
    KEYBOARD_ERROR = ""
except Exception as exc:
    keyboard_lib = None
    KEYBOARD_OK = False
    KEYBOARD_ERROR = str(exc)

try:
    import obsws_python as obsws
    OBSWS_OK = True
    OBSWS_ERROR = ""
except Exception as exc:
    obsws = None
    OBSWS_OK = False
    OBSWS_ERROR = str(exc)

APP_NAME = "SATURN Control"
APP_VERSION = "1.1.0-linux"
BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
CONFIG_PATH = BASE_DIR / "config.json"

app = Flask(__name__, static_folder=str(WEB_DIR))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading") if SocketIO else None

_config_cache = None
_config_lock = threading.Lock()

runtime = {
    "app": APP_NAME,
    "version": APP_VERSION,
    "os": platform.system(),
    "platform": platform.platform(),
    "session": os.environ.get("XDG_SESSION_TYPE", "unknown"),
    "desktop": os.environ.get("XDG_CURRENT_DESKTOP", os.environ.get("DESKTOP_SESSION", "unknown")),
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


def add_event(kind, message, **extra):
    item = {
        "time": time.strftime("%H:%M:%S"),
        "kind": kind,
        "message": message,
        **extra,
    }
    runtime["events"].insert(0, item)
    runtime["events"] = runtime["events"][:80]
    print(f"[SATURN] {message}")
    if socketio:
        socketio.emit("saturn_event", item)
    return item


def command_exists(name):
    return shutil.which(name) is not None


def run_command(args, *, shell=False, cwd=None, timeout=4):
    """Run a small command and return (ok, message)."""
    try:
        if shell:
            proc = subprocess.run(
                args,
                shell=True,
                cwd=cwd,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
            )
        else:
            proc = subprocess.run(
                args,
                shell=False,
                cwd=cwd,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
            )
        output = (proc.stdout or proc.stderr or "").strip()
        return proc.returncode == 0, output
    except Exception as exc:
        return False, str(exc)


def run_detached(args, *, shell=False, cwd=None):
    try:
        subprocess.Popen(
            args,
            shell=shell,
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
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
    if command_exists("xdg-open"):
        return run_detached(["xdg-open", target])
    return False, "xdg-open no está instalado"


DEFAULT_CONFIG = {
    "active_profile": "media",
    "settings": {
        "debounce_ms": 100,
        "open_browser_on_start": True,
        "theme": "saturn-dark",
    },
    "obs": {
        "host": "localhost",
        "password": "",
        "port": 4455,
    },
    "profiles": {
        "media": {
            "name": "Media",
            "buttons": {
                "1": {"label": "Play / Pause", "key": "F13", "action": "play_pause", "params": {}},
                "2": {"label": "Anterior", "key": "F14", "action": "prev_track", "params": {}},
                "3": {"label": "Siguiente", "key": "F15", "action": "next_track", "params": {}},
                "4": {"label": "Silenciar", "key": "F16", "action": "mute", "params": {}},
                "5": {"label": "Volumen −", "key": "F17", "action": "volume_down", "params": {}},
                "6": {"label": "Volumen +", "key": "F18", "action": "volume_up", "params": {}},
            },
        },
        "stream": {
            "name": "Stream",
            "buttons": {
                "1": {"label": "Escena Juego", "key": "F13", "action": "obs_scene", "params": {"scene": "Juegos"}},
                "2": {"label": "Escena Cámara", "key": "F14", "action": "obs_scene", "params": {"scene": "Cámara"}},
                "3": {"label": "BRB", "key": "F15", "action": "obs_scene", "params": {"scene": "BRB"}},
                "4": {"label": "Mic", "key": "F16", "action": "mute_mic", "params": {}},
                "5": {"label": "Grabar", "key": "F17", "action": "obs_start_record", "params": {}},
                "6": {"label": "Detener", "key": "F18", "action": "obs_stop_record", "params": {}},
            },
        },
        "work": {
            "name": "Trabajo",
            "buttons": {
                "1": {"label": "VS Code", "key": "F13", "action": "open_vscode", "params": {}},
                "2": {"label": "Terminal", "key": "F14", "action": "open_terminal", "params": {}},
                "3": {"label": "Carpeta", "key": "F15", "action": "file_explorer", "params": {}},
                "4": {"label": "Navegador", "key": "F16", "action": "open_browser", "params": {}},
                "5": {"label": "Captura", "key": "F17", "action": "screenshot", "params": {}},
                "6": {"label": "GitHub", "key": "F18", "action": "custom_url", "params": {"url": "https://github.com/franduartedev"}},
            },
        },
        "fdlabs": {
            "name": "FD Labs",
            "buttons": {
                "1": {"label": "ATLAS", "key": "F13", "action": "open_folder", "params": {"path": str(Path.home())}},
                "2": {"label": "Obsidian", "key": "F14", "action": "open_obsidian", "params": {}},
                "3": {"label": "YouTube", "key": "F15", "action": "custom_url", "params": {"url": "https://www.youtube.com"}},
                "4": {"label": "GitHub", "key": "F16", "action": "custom_url", "params": {"url": "https://github.com/franduartedev"}},
                "5": {"label": "Terminal", "key": "F17", "action": "open_terminal", "params": {}},
                "6": {"label": "Música", "key": "F18", "action": "play_pause", "params": {}},
            },
        },
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
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)


def load_config():
    global _config_cache
    ensure_config_file()
    with _config_lock:
        if _config_cache is None:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            _config_cache = deep_merge(DEFAULT_CONFIG, loaded)
            active = _config_cache.get("active_profile")
            if active not in _config_cache.get("profiles", {}):
                _config_cache["active_profile"] = "media"
        return _config_cache


def save_config(data):
    global _config_cache
    if "profiles" not in data or not data["profiles"]:
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


def normalize_key(value):
    """Normalize key names coming from Linux listeners into f13..f18."""
    if value is None:
        return ""
    s = str(value).strip().lower().replace("'", "").replace('"', "").replace(" ", "")
    s = s.strip("<>")
    s = s.replace("key.", "").replace("key_", "").replace("key-", "")

    match = re.search(r"f(1[3-8])", s)
    if match:
        return f"f{match.group(1)}"

    evdev_codes = {
        "183": "f13",
        "184": "f14",
        "185": "f15",
        "186": "f16",
        "187": "f17",
        "188": "f18",
    }
    if s in evdev_codes:
        return evdev_codes[s]

    # XFCE/X11 through pynput can expose F13-F18 as XF86 keysyms.
    x11_keysyms = {
        "269025153": "f13",  # XF86Tools
        "269025093": "f14",  # XF86Launch5
        "269025094": "f15",  # XF86Launch6
        "269025095": "f16",  # XF86Launch7
        "269025096": "f17",  # XF86Launch8
        "269025097": "f18",  # XF86Launch9
    }
    if s in x11_keysyms:
        return x11_keysyms[s]

    hid_codes = {
        "70068": "f13",
        "70069": "f14",
        "7006a": "f15",
        "7006b": "f16",
        "7006c": "f17",
        "7006d": "f18",
    }
    if s in hid_codes:
        return hid_codes[s]
    return s


def button_map_from_config():
    mapping = {}
    for btn_id, btn in get_active_buttons().items():
        fallback = f"F{12 + int(btn_id)}" if str(btn_id).isdigit() else ""
        key = normalize_key(btn.get("key") or fallback)
        if key:
            mapping[key] = str(btn_id)
    mapping.setdefault("f13", "1")
    mapping.setdefault("f14", "2")
    mapping.setdefault("f15", "3")
    mapping.setdefault("f16", "4")
    mapping.setdefault("f17", "5")
    mapping.setdefault("f18", "6")
    return mapping


ACTION_CATALOG = [
    {"id": "play_pause", "name": "Play / Pause", "category": "Multimedia", "icon": "play", "description": "Alterna reproducción del reproductor activo.", "fields": []},
    {"id": "next_track", "name": "Siguiente", "category": "Multimedia", "icon": "skip-forward", "description": "Pasa a la siguiente pista/video.", "fields": []},
    {"id": "prev_track", "name": "Anterior", "category": "Multimedia", "icon": "skip-back", "description": "Vuelve a la pista/video anterior.", "fields": []},
    {"id": "volume_up", "name": "Subir volumen", "category": "Audio", "icon": "volume-2", "description": "Sube el volumen del sistema.", "fields": []},
    {"id": "volume_down", "name": "Bajar volumen", "category": "Audio", "icon": "volume-1", "description": "Baja el volumen del sistema.", "fields": []},
    {"id": "mute", "name": "Silenciar audio", "category": "Audio", "icon": "volume-x", "description": "Alterna mute del audio principal.", "fields": []},
    {"id": "mute_mic", "name": "Silenciar micrófono", "category": "Audio", "icon": "mic-off", "description": "Alterna mute del micrófono del sistema.", "fields": []},
    {"id": "open_browser", "name": "Abrir navegador", "category": "Apps", "icon": "globe", "description": "Abre el navegador predeterminado.", "fields": []},
    {"id": "open_chrome", "name": "Abrir Chrome/Chromium", "category": "Apps", "icon": "globe", "description": "Intenta abrir Chrome, Chromium, Brave o Firefox.", "fields": []},
    {"id": "open_obs", "name": "Abrir OBS", "category": "Apps", "icon": "broadcast", "description": "Abre OBS Studio si está instalado.", "fields": []},
    {"id": "open_vscode", "name": "Abrir VS Code", "category": "Apps", "icon": "code", "description": "Abre VS Code / Codium.", "fields": []},
    {"id": "open_discord", "name": "Abrir Discord", "category": "Apps", "icon": "message", "description": "Abre Discord si está instalado.", "fields": []},
    {"id": "open_spotify", "name": "Abrir Spotify", "category": "Apps", "icon": "music", "description": "Abre Spotify si está instalado.", "fields": []},
    {"id": "open_telegram", "name": "Abrir Telegram", "category": "Apps", "icon": "send", "description": "Abre Telegram Desktop.", "fields": []},
    {"id": "open_terminal", "name": "Abrir terminal", "category": "Sistema", "icon": "terminal", "description": "Abre una terminal compatible con tu escritorio.", "fields": []},
    {"id": "file_explorer", "name": "Abrir home", "category": "Sistema", "icon": "folder", "description": "Abre tu carpeta personal.", "fields": []},
    {"id": "open_folder", "name": "Abrir carpeta", "category": "Sistema", "icon": "folder-open", "description": "Abre una carpeta específica.", "fields": [{"name": "path", "label": "Ruta", "type": "text", "placeholder": "/home/fran/Proyecto"}]},
    {"id": "screenshot", "name": "Captura de pantalla", "category": "Sistema", "icon": "camera", "description": "Abre herramienta de captura disponible.", "fields": []},
    {"id": "custom_url", "name": "Abrir URL", "category": "Web", "icon": "link", "description": "Abre una página o panel web.", "fields": [{"name": "url", "label": "URL", "type": "url", "placeholder": "https://..."}]},
    {"id": "custom_hotkey", "name": "Atajo de teclado", "category": "Sistema", "icon": "keyboard", "description": "Envía una combinación mediante xdotool.", "fields": [{"name": "hotkey", "label": "Atajo", "type": "text", "placeholder": "ctrl+shift+p"}]},
    {"id": "type_text", "name": "Escribir texto", "category": "Sistema", "icon": "text", "description": "Escribe texto en la ventana activa.", "fields": [{"name": "text", "label": "Texto", "type": "textarea", "placeholder": "Texto a escribir"}]},
    {"id": "run_command", "name": "Comando", "category": "Avanzado", "icon": "terminal-square", "description": "Ejecuta un comando del sistema.", "fields": [{"name": "command", "label": "Comando", "type": "text", "placeholder": "echo hola"}, {"name": "cwd", "label": "Carpeta de trabajo", "type": "text", "placeholder": "/home/fran"}]},
    {"id": "obs_scene", "name": "OBS: cambiar escena", "category": "OBS", "icon": "broadcast", "description": "Cambia la escena activa por WebSocket.", "fields": [{"name": "scene", "label": "Escena", "type": "text", "placeholder": "Juegos"}]},
    {"id": "obs_start_record", "name": "OBS: iniciar grabación", "category": "OBS", "icon": "record", "description": "Inicia grabación en OBS.", "fields": []},
    {"id": "obs_stop_record", "name": "OBS: detener grabación", "category": "OBS", "icon": "stop", "description": "Detiene grabación en OBS.", "fields": []},
    {"id": "obs_start_stream", "name": "OBS: iniciar stream", "category": "OBS", "icon": "radio", "description": "Inicia stream en OBS.", "fields": []},
    {"id": "obs_stop_stream", "name": "OBS: detener stream", "category": "OBS", "icon": "stop", "description": "Detiene stream en OBS.", "fields": []},
    {"id": "obs_toggle_mute_mic", "name": "OBS: mute input", "category": "OBS", "icon": "mic-off", "description": "Alterna mute de una fuente de audio en OBS.", "fields": [{"name": "input", "label": "Nombre del input", "type": "text", "placeholder": "Mic/Aux"}]},
]


def action_meta(action_id):
    return next((a for a in ACTION_CATALOG if a["id"] == action_id), None)


def linux_media(action):
    if action == "play_pause":
        if command_exists("playerctl"):
            return run_command(["playerctl", "play-pause"], timeout=3)
        if command_exists("xdotool"):
            return run_command(["xdotool", "key", "XF86AudioPlay"], timeout=3)
        return False, "Falta playerctl o xdotool"

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
        return False, "Falta wpctl o pactl"

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
            return run_command(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"], timeout=3)
        return False, "Falta wpctl o pactl"

    return False, "Acción multimedia desconocida"


def obs_request(method, params=None):
    if not OBSWS_OK:
        return False, f"obsws-python no disponible: {OBSWS_ERROR}"
    try:
        cfg = load_config().get("obs", {})
        cl = obsws.ReqClient(
            host=cfg.get("host", "localhost"),
            port=int(cfg.get("port", 4455)),
            password=cfg.get("password", ""),
            timeout=3,
        )
        fn = getattr(cl, method)
        result = fn(**(params or {}))
        try:
            cl.disconnect()
        except Exception:
            pass
        return True, str(result or "ok")
    except Exception as exc:
        return False, str(exc)


def execute_action(action, params=None):
    params = params or {}
    runtime["last_action"] = action
    meta = action_meta(action)
    action_name = meta["name"] if meta else action

    try:
        ok, detail = True, "ok"
        if action in {"play_pause", "next_track", "prev_track", "volume_up", "volume_down", "mute", "mute_mic"}:
            ok, detail = linux_media(action)

        elif action == "custom_url":
            url = params.get("url", "").strip()
            ok, detail = xdg_open(url) if url else (False, "URL vacía")

        elif action == "open_youtube":
            ok, detail = xdg_open("https://www.youtube.com")

        elif action == "open_twitch":
            ok, detail = xdg_open("https://www.twitch.tv")

        elif action in {"open_browser", "open_chrome"}:
            cmd = first_existing_command([["google-chrome"], ["chromium"], ["brave-browser"], ["firefox"]])
            ok, detail = run_detached(cmd) if cmd else xdg_open("https://www.google.com")

        elif action == "file_explorer":
            ok, detail = xdg_open(str(Path.home()))

        elif action == "open_folder":
            path = params.get("path", "").strip() or str(Path.home())
            ok, detail = xdg_open(path)

        elif action == "open_obsidian":
            cmd = first_existing_command([["obsidian"], ["flatpak", "run", "md.obsidian.Obsidian"]])
            ok, detail = run_detached(cmd) if cmd else (False, "No encontré Obsidian")

        elif action == "open_obs":
            cmd = first_existing_command([["obs"], ["flatpak", "run", "com.obsproject.Studio"]])
            ok, detail = run_detached(cmd) if cmd else (False, "No encontré OBS")

        elif action == "open_vscode":
            cmd = first_existing_command([["code"], ["codium"], ["flatpak", "run", "com.visualstudio.code"]])
            ok, detail = run_detached(cmd) if cmd else (False, "No encontré VS Code/Codium")

        elif action == "open_discord":
            cmd = first_existing_command([["discord"], ["flatpak", "run", "com.discordapp.Discord"]])
            ok, detail = run_detached(cmd) if cmd else (False, "No encontré Discord")

        elif action == "open_steam":
            cmd = first_existing_command([["steam"], ["flatpak", "run", "com.valvesoftware.Steam"]])
            ok, detail = run_detached(cmd) if cmd else (False, "No encontré Steam")

        elif action == "open_spotify":
            cmd = first_existing_command([["spotify"], ["flatpak", "run", "com.spotify.Client"]])
            ok, detail = run_detached(cmd) if cmd else (False, "No encontré Spotify")

        elif action == "open_telegram":
            cmd = first_existing_command([["telegram-desktop"], ["flatpak", "run", "org.telegram.desktop"]])
            ok, detail = run_detached(cmd) if cmd else (False, "No encontré Telegram")

        elif action == "open_terminal":
            cmd = first_existing_command([["xfce4-terminal"], ["x-terminal-emulator"], ["gnome-terminal"], ["konsole"], ["alacritty"], ["kitty"]])
            ok, detail = run_detached(cmd) if cmd else (False, "No encontré terminal compatible")

        elif action == "screenshot":
            cmd = first_existing_command([["xfce4-screenshooter"], ["gnome-screenshot", "-i"], ["flameshot", "gui"], ["spectacle"]])
            ok, detail = run_detached(cmd) if cmd else (False, "No encontré herramienta de captura")

        elif action == "run_command":
            cmd = params.get("command", "").strip()
            cwd = params.get("cwd", "").strip() or None
            ok, detail = run_detached(cmd, shell=True, cwd=cwd) if cmd else (False, "Comando vacío")

        elif action == "custom_hotkey":
            hotkey = params.get("hotkey", "").strip()
            if hotkey and command_exists("xdotool"):
                ok, detail = run_command(["xdotool", "key", hotkey], timeout=3)
            else:
                ok, detail = False, "Falta xdotool o atajo vacío"

        elif action == "type_text":
            text = params.get("text", "")
            if text and command_exists("xdotool"):
                ok, detail = run_command(["xdotool", "type", "--clearmodifiers", text], timeout=3)
            else:
                ok, detail = False, "Falta xdotool o texto vacío"

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
    runtime["last_key"] = key
    runtime["last_raw_key"] = str(raw if raw is not None else key_name)
    mapping = button_map_from_config()
    btn_id = mapping.get(key)
    if not btn_id:
        add_event("key", f"Tecla detectada sin mapa: {key}", key=key, raw=runtime["last_raw_key"])
        return

    runtime["last_button"] = btn_id
    btn_cfg = get_active_buttons().get(str(btn_id), {})
    action = btn_cfg.get("action")
    params = btn_cfg.get("params", {})
    label = btn_cfg.get("label", f"Botón {btn_id}")
    add_event("button", f"{key.upper()} → Botón {btn_id}: {label}", key=key, button=btn_id, action=action)
    if socketio:
        socketio.emit("button_press", {"id": int(btn_id)})
    if action:
        threading.Thread(target=execute_action, args=(action, params), daemon=True).start()


def start_pynput_listener():
    last_fire = {}
    debounce = max(20, int(load_config().get("settings", {}).get("debounce_ms", 100))) / 1000

    def on_press(key):
        raw = str(key)
        try:
            name = key.name
        except AttributeError:
            name = getattr(key, "char", None) or raw
        norm = normalize_key(name)
        now = time.monotonic()
        if now - last_fire.get(norm, 0) < debounce:
            return
        last_fire[norm] = now
        handle_key_name(norm, raw=raw)

    listener = pynput_keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()
    runtime["listener_backend"] = "pynput"
    runtime["listener_ok"] = True
    add_event("status", "Listener iniciado con pynput")


def start_keyboard_lib_listener():
    last_fire = {}
    debounce = max(20, int(load_config().get("settings", {}).get("debounce_ms", 100))) / 1000

    def on_key(event):
        if getattr(event, "event_type", "down") != "down":
            return
        norm = normalize_key(event.name)
        now = time.monotonic()
        if now - last_fire.get(norm, 0) < debounce:
            return
        last_fire[norm] = now
        handle_key_name(norm, raw=event.name)

    keyboard_lib.on_press(on_key)
    runtime["listener_backend"] = "keyboard"
    runtime["listener_ok"] = True
    add_event("status", "Listener iniciado con keyboard")


def start_keyboard_listener():
    if PYNPUT_OK:
        try:
            start_pynput_listener()
            return
        except Exception as exc:
            runtime["listener_error"] = str(exc)
            add_event("error", f"No pude iniciar pynput: {exc}")
    else:
        runtime["listener_error"] = PYNPUT_ERROR
        add_event("error", f"pynput no disponible: {PYNPUT_ERROR}")

    if KEYBOARD_OK:
        try:
            start_keyboard_lib_listener()
            return
        except Exception as exc:
            runtime["listener_error"] = str(exc)
            add_event("error", f"No pude iniciar keyboard: {exc}")
    else:
        runtime["listener_error"] = KEYBOARD_ERROR
        add_event("error", f"keyboard no disponible: {KEYBOARD_ERROR}")

    runtime["listener_backend"] = "none"
    runtime["listener_ok"] = False
    add_event("error", "No se pudo iniciar ningún listener de teclado")


def system_dependencies():
    return {
        "python3": command_exists("python3"),
        "playerctl": command_exists("playerctl"),
        "pactl": command_exists("pactl"),
        "wpctl": command_exists("wpctl"),
        "xdotool": command_exists("xdotool"),
        "xdg-open": command_exists("xdg-open"),
        "evtest": command_exists("evtest"),
        "lsusb": command_exists("lsusb"),
        "pynput": PYNPUT_OK,
        "keyboard": KEYBOARD_OK,
        "obsws-python": OBSWS_OK,
    }


@app.route("/")
def index():
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
    return jsonify({
        **runtime,
        "dependencies": system_dependencies(),
        "active_profile": active_profile_id(),
        "key_map": button_map_from_config(),
        "config_path": str(CONFIG_PATH),
        "web_dir": str(WEB_DIR),
    })


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
        cfg["obs"] = {
            "host": data.get("host", cfg.get("obs", {}).get("host", "localhost")),
            "port": int(data.get("port", cfg.get("obs", {}).get("port", 4455))),
            "password": data.get("password", cfg.get("obs", {}).get("password", "")),
        }
        ok, detail = obs_request("get_version")
        return jsonify({"ok": ok, "message": detail})
    except Exception as exc:
        return jsonify({"ok": False, "message": str(exc)})


def open_browser_later():
    if not load_config().get("settings", {}).get("open_browser_on_start", True):
        return
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    print("╔══════════════════════════════════════╗")
    print("║          SATURN Control v1.1         ║")
    print("║       FD Labs · Linux Edition        ║")
    print("╚══════════════════════════════════════╝")
    print(f"Config : {CONFIG_PATH}")
    print("URL    : http://127.0.0.1:5000")
    print(f"Sesión : {runtime['session']} / {runtime['desktop']}\n")
    start_keyboard_listener()
    threading.Thread(target=open_browser_later, daemon=True).start()
    if socketio:
        socketio.run(app, host="127.0.0.1", port=5000, debug=False, allow_unsafe_werkzeug=True)
    else:
        app.run(host="127.0.0.1", port=5000, debug=False)
