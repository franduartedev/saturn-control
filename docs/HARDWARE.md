# Hardware SATURN v1

El deck SATURN v1 es simple a propósito: pocos componentes, fáciles de conseguir y de soldar.

## Lista de materiales

| Cant | Componente | Notas |
| ---: | --- | --- |
| 1 | Arduino Pro Micro (ATmega32U4, 5V/16MHz) o Leonardo compatible | USB nativo para HID |
| 6 | Pulsadores momentáneos NA | Los del deck físico |
| — | Cables, protoboard o placa + soldadura | Una pata por pin, otra a GND común |
| 1 | Cable micro-USB de datos | Que no sea solo de carga |
| 1 | PC con Windows o Linux | Corre la app + panel web |

Opcional: carcasa, keycaps impresas en 3D (ver [`KEYCAPS.md`](KEYCAPS.md)).

## Por qué el Pro Micro

El ATmega32U4 tiene USB nativo y, con `Keyboard.h`, el sistema lo reconoce como **teclado HID** (en Linux aparece como `Arduino Leonardo`). No necesitás drivers raros ni software extra: lo enchufás y ya manda teclas.

## Por qué F13–F18

Son teclas reales del estándar HID que casi ningún programa usa. Así tus botones no pisan `Ctrl+C`, `Alt+Tab` ni nada cotidiano. El firmware manda **taps cortos** (14 ms) con debounce de 25 ms y loop no bloqueante, así cada toque es un disparo limpio.

El sketch vive en `firmware/saturn_pro_micro/saturn_pro_micro.ino` y su detalle (tap, repetición opcional apagada por defecto, LED de actividad, debug serial) está en [`../firmware/README.md`](../firmware/README.md).

## Alimentación y USB

Se alimenta directo del USB (5V). No lleva fuente externa. Usá un cable micro-USB **de datos**: los de solo-carga son la causa número uno de "no lo detecta".

## Notas por sistema operativo

- **Windows**: HID directo, sin dependencias del sistema. La config queda en `%APPDATA%\SATURN Control\config.json`.
- **Linux X11 (validado Arch + XFCE)**: el listener `pynput` a veces entrega F13–F18 como keysyms raros; la app los normaliza (evdev 183–188, keysyms, HID 0x68–0x6D). Multimedia por `playerctl`, volumen por `wpctl` → `pactl`, hotkeys por `xdotool`.
- **Linux Wayland**: el listener global puede estar limitado por el compositor. El panel lo avisa en Diagnóstico. Si podés, usá sesión X11 para el deck.

El cableado físico, con el GND común explicado paso a paso, está en [`WIRING.md`](WIRING.md).
