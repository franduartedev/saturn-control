# SATURN Control v1.1 · Linux

## Arranque

```bash
chmod +x *.sh
./diagnose_linux.sh
./launch_linux.sh
```

Panel local:

```text
http://127.0.0.1:5000
```

## Dependencias recomendadas en Arch/XFCE

```bash
sudo pacman -S --needed python python-pip tk playerctl wireplumber xdotool xdg-utils evtest usbutils
```

## Test del Pro Micro

```bash
sudo evtest
```

Elegí `Arduino Leonardo` y verificá:

```text
KEY_F13
KEY_F14
KEY_F15
KEY_F16
KEY_F17
KEY_F18
```

## Notas

- En X11/XFCE, `pynput` puede entregar F13-F18 como keysyms raros. SATURN v1.1 ya normaliza esos códigos.
- Para multimedia usá `playerctl`.
- Para volumen usá `wpctl`/WirePlumber o `pactl`.
- En Wayland puede haber restricciones para escuchar teclas globales.
