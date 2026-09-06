from pynput import keyboard

print('SATURN key watcher')
print('Apretá los botones del Pro Micro. Ctrl+C para salir.\n')

def on_press(key):
    try:
        name = key.name
    except AttributeError:
        name = key.char
    print(f'Detectado: {name}')

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
