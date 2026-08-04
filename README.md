# SATURN Control

**SATURN Control** es un sistema de software y hardware para configurar y utilizar un stream deck casero construido con un **Arduino Pro Micro** y botones físicos.

El proyecto forma parte de **FD Labs**, mi laboratorio personal de software, electrónica, automatización y herramientas propias.

> Proyecto personal desarrollado con asistencia de herramientas de inteligencia artificial. Mi trabajo incluyó el diseño y armado del dispositivo físico, la definición del producto, la arquitectura funcional, las pruebas de integración, la detección de errores y la iteración del software.

## Estado del proyecto

**Versión estable inicial:** `1.0.0`

La versión actual funciona como una primera base distribuible y como proyecto de portfolio. Todavía no se considera un producto comercial terminado.

## El problema

Los stream decks comerciales permiten ejecutar acciones rápidas desde botones físicos, pero suelen tener un costo elevado. SATURN nació como una alternativa casera y personalizable, construida con componentes accesibles y software propio.

## Qué permite hacer

- Detectar seis botones físicos como teclas HID `F13` a `F18`.
- Configurar acciones desde una interfaz visual.
- Crear y cambiar perfiles de macros.
- Diagnosticar las teclas recibidas desde el dispositivo.
- Ejecutar acciones multimedia y del sistema.
- Abrir aplicaciones, sitios web y herramientas de desarrollo.
- Controlar acciones relacionadas con OBS y streaming.
- Ejecutar comandos personalizados.
- Utilizar el dispositivo tanto en Windows como en Linux.

## Arquitectura general

SATURN combina tres partes:

1. **Hardware:** Arduino Pro Micro y seis botones físicos.
2. **Firmware:** convierte las pulsaciones en teclas HID.
3. **Aplicación de escritorio:** interpreta las teclas y ejecuta las acciones configuradas.

### Estructura principal

- `app.py`: servidor local Flask y lógica de macros.
- `desktop_app.py`: aplicación de escritorio con la interfaz integrada.
- `web/`: interfaz visual de configuración.
- `firmware/`: código para Arduino Pro Micro.
- `installer/`: configuración del instalador para Windows.
- `tools/`: utilidades de compilación y recursos.

## Hardware utilizado

| Componente | Función |
| --- | --- |
| Arduino Pro Micro ATmega32U4 | Controlador USB HID |
| 6 botones físicos | Entradas del stream deck |
| PC con Windows o Linux | Ejecuta SATURN Control |

### Mapeo predeterminado

| Botón | Pin del Pro Micro | Tecla enviada |
| --- | ---: | --- |
| 1 | 2 | F13 |
| 2 | 3 | F14 |
| 3 | 4 | F15 |
| 4 | 5 | F16 |
| 5 | 6 | F17 |
| 6 | 7 | F18 |

Cada botón se conecta entre su pin y `GND`. El firmware utiliza `INPUT_PULLUP`.

## Tecnologías utilizadas

- Python
- Flask
- HTML, CSS y JavaScript
- Arduino / C++
- HID USB
- PyInstaller
- Inno Setup
- Git y GitHub

## Ejecutar en Windows durante desarrollo

```bat
launch_desktop.bat
```

## Generar el instalador para Windows

```bat
build_release_winteros.bat
```

El instalador generado queda en:

```text
release\SATURN-Control-Setup-1.0.0.exe
```

El usuario final no necesita instalar Python, pip, PyInstaller ni Inno Setup.

## Ejecutar en Linux

```bash
chmod +x launch_linux.sh
./launch_linux.sh
```

La guía completa está en [README_LINUX.md](README_LINUX.md).

## Qué aprendí con este proyecto

- Integración entre software y hardware.
- Funcionamiento básico de un dispositivo HID USB.
- Diseño de una herramienta a partir de una necesidad real.
- Pruebas con botones, eventos y perfiles configurables.
- Distribución de una aplicación de escritorio en Windows.
- Compatibilidad básica entre Windows y Linux.
- Uso de IA como herramienta de apoyo para desarrollar, probar e iterar un producto propio.

## Documentación

- [CHANGELOG.md](CHANGELOG.md)
- [ROADMAP.md](ROADMAP.md)
- [AUTHORSHIP.md](AUTHORSHIP.md)
- [README_WINDOWS_EXE.md](README_WINDOWS_EXE.md)
- [README_DISTRIBUCION.md](README_DISTRIBUCION.md)
- [firmware/README.md](firmware/README.md)

## Autoría y asistencia de IA

SATURN Control fue ideado, construido, probado y dirigido por **Francisco Duarte** bajo la identidad de **FD Labs**.

El desarrollo del software y parte de la documentación contó con asistencia de herramientas de inteligencia artificial. Las decisiones de producto, el armado físico, la selección de componentes, las pruebas funcionales, la detección de errores y la validación del sistema fueron realizadas por el autor.

## Licencia

Consultar el archivo [LICENSE](LICENSE).

---

SATURN Control es una muestra de cómo combinar programación, electrónica y experimentación para construir una herramienta útil con recursos accesibles.
