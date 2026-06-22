# Firmware SATURN Pro Micro

Este sketch es para un Arduino Pro Micro / Leonardo compatible.

## Qué trae esta versión

- Lectura estable con `INPUT_PULLUP`.
- Taps cortos de tecla, sin dejar teclas sostenidas.
- Loop no bloqueante, sin `delay()`.
- LED de actividad al detectar pulsaciones.
- Tabla única por botón para evitar mezclar pines y teclas.
- Repetición por botón disponible, apagada por defecto.
- Debug por serial disponible, apagado por defecto.

## Cableado esperado

Cada botón va entre el pin indicado y GND. El sketch usa `INPUT_PULLUP`, así que no necesita resistencias externas.
Cuando detecta una pulsación, manda un toque corto de tecla y la libera automáticamente.

| Botón físico | Pin Pro Micro | Tecla enviada |
| --- | --- | --- |
| 1 | 2 | F13 |
| 2 | 3 | F14 |
| 3 | 4 | F15 |
| 4 | 5 | F16 |
| 5 | 6 | F17 |
| 6 | 7 | F18 |

Si usaste otros pines, cambiá solo la tabla `BUTTONS` en `saturn_pro_micro/saturn_pro_micro.ino`.

## Ajustes rápidos

En el sketch podés tocar estos valores:

| Ajuste | Valor actual | Para qué sirve |
| --- | ---: | --- |
| `DEBOUNCE_MS` | 25 | Filtra rebotes del botón físico. |
| `TAP_MS` | 14 | Tiempo que la tecla queda presionada antes de soltarse. |
| `LED_PULSE_MS` | 70 | Duración del parpadeo del LED al pulsar. |
| `ENABLE_SERIAL_DEBUG` | 0 | Si lo ponés en 1, imprime botones por monitor serial. |
| `ENABLE_ACTIVITY_LED` | 1 | Si lo ponés en 0, apaga el LED de actividad. |

## Repetición al mantener presionado

Por defecto todos los botones tienen repetición apagada:

```cpp
{2, KEY_F13, false, 450, 120}
```

El tercer valor controla si repite mientras mantenés presionado. Para activar repetición en un botón, cambiá `false` por `true`.

Ejemplo:

```cpp
{6, KEY_F17, true, 450, 120}
```

Eso espera 450 ms y después repite cada 120 ms mientras el botón siga apretado.

## Si F17 y F18 se intercalan

1. Cargá este sketch.
2. Abrí SATURN y entrá a `Diagnóstico`.
3. Tocá varias veces el botón físico 5.
4. Debe aparecer siempre `F17`.
5. Tocá varias veces el botón físico 6.
6. Debe aparecer siempre `F18`.

Si el mismo botón sigue alternando entre `F17` y `F18`, revisá que los cables de los pines 6 y 7 no estén tocándose, que cada botón tenga una pata a GND y la otra a su pin, y que no haya una soldadura fría.

## Si tarda en volver a tomar pulsaciones

Usá esta versión del sketch. Está en modo `tap`: no deja la tecla sostenida hasta que soltás el botón, sino que envía una pulsación corta y libera la tecla automáticamente.
