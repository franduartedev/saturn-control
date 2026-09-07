# Cableado SATURN v1 (Wiring)

Regla de oro: **cada botón va entre un pin digital y GND**. Sin resistencias externas, porque usamos `INPUT_PULLUP`.

## Cómo funciona el INPUT_PULLUP

El sketch configura cada pin como `INPUT_PULLUP`, o sea con una resistencia interna que lo mantiene en HIGH cuando nadie lo toca.

- En reposo: el pin lee HIGH.
- Apretás el botón: conectás el pin a GND → lee LOW.
- El firmware detecta ese flanco, filtra el rebote (25 ms) y manda un tap corto de la tecla.

Por eso cada pulsador lleva **una pata al pin y la otra al GND**. Nada más.

## GND común compartido

Los 6 pulsadores **comparten el mismo GND**. No necesitás 6 tierras distintas: conectás una pata de cada botón al GND del Pro Micro (podés encadenarlos en serie con un solo cable que los recorre a todos) y la otra pata a su pin correspondiente.

```text
Pin 2 ----[Botón 1]----+
Pin 3 ----[Botón 2]----+---- GND del Pro Micro
Pin 4 ----[Botón 3]----+
Pin 5 ----[Botón 4]----+
Pin 6 ----[Botón 5]----+
Pin 7 ----[Botón 6]----+
```

## Tabla botón / pin / tecla

| Botón | Pin Pro Micro | Tecla enviada | Uso típico (perfil Media) |
| ---: | --- | --- | --- |
| 1 | 2 | F13 | PLAY |
| 2 | 3 | F14 | PREV |
| 3 | 4 | F15 | NEXT |
| 4 | 5 | F16 | MUTE |
| 5 | 6 | F17 | VOL− |
| 6 | 7 | F18 | VOL+ |

Si tu protoboard usa otros pines, cambiá solo la tabla `BUTTONS` en `firmware/saturn_pro_micro/saturn_pro_micro.ino`. La app mapea por tecla (`F13`–`F18`), no por pin, así que del lado software no cambia nada.

## Tips de soldado y pruebas

1. Primero probá en protoboard sin soldar.
2. Verificá con `sudo evtest` (Linux) que aparezcan `KEY_F13`…`KEY_F18`, o mirá la vista Diagnóstico del panel (última tecla + raw).
3. Si F17 y F18 se intercalan: revisá que los cables de pines 6 y 7 no se toquen, que cada botón tenga una pata a GND y la otra a su pin, y que no haya soldadura fría (detalle original en [`../firmware/README.md`](../firmware/README.md)).
4. Si hay doble disparo: subí `DEBOUNCE_MS` (25 por defecto) de a 5 ms.
5. Si algún botón no responde: medí continuidad entre su pin y GND al apretarlo.

Con esto el hardware queda listo. El resto (qué hace cada botón) se configura por perfil en el panel web.
