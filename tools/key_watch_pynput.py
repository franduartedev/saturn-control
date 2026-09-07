"""SATURN key watcher — diagnóstico F13-F18 (Linux/X11 + Windows)."""
import sys
sys.path.insert(0, "..")
try:
    from app import normalize_key
except Exception:
    def normalize_key(v):
        return str(v or "").lower()

from pynput import keyboard

print("SATURN key watcher v1.1.1")
print("Apretá los botones del Pro Micro. Ctrl+C para salir.")
print("Esperado: F13..F18 (evdev 183..188, keysyms XFCE o HID 0x68..0x6D).\n")


def on_press(key):
    try:
        name = key.name
    except AttributeError:
        name = getattr(key, "char", None) or str(key)
    print(f"Detectado: {name} -> normalizado: {normalize_key(name)} (raw: {key})")


with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
