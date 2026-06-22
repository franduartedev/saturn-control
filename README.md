# SATURN Control

SATURN Control es una aplicación de escritorio para configurar y usar un macro deck físico casero basado en Arduino Pro Micro.

El proyecto forma parte de **FD Labs**, el laboratorio personal de Francisco Duarte para electrónica, software, streaming, robótica y herramientas propias.

## Estado

Versión estable inicial: **1.0.0**

Este repositorio se publica como proyecto personal/portfolio. No es todavía un producto comercial final.

## Qué hace

- Escucha botones físicos enviados como teclas HID `F13` a `F18`.
- Permite configurar macros desde una interfaz visual.
- Soporta perfiles de macros.
- Incluye diagnóstico de teclas detectadas.
- Permite acciones multimedia, sistema, apps, web, OBS, VS Code y comandos personalizados.
- Incluye firmware para Arduino Pro Micro.
- Incluye build Windows con instalador.
- Incluye scripts para Linux.

## Vista general

SATURN está compuesto por:

- `app.py`: servidor local Flask + lógica de macros.
- `desktop_app.py`: ventana de escritorio con la UI integrada.
- `web/`: interfaz visual.
- `firmware/`: sketch para Arduino Pro Micro.
- `installer/`: configuración del instalador Windows.
- `tools/`: utilidades de build e icono.

## Hardware base

| Componente | Uso |
| --- | --- |
| Arduino Pro Micro | Controlador HID USB |
| 6 botones físicos | Entrada del macro deck |
| PC Windows/Linux | Ejecuta SATURN Control |

Mapeo por defecto del firmware:

| Botón | Pin Pro Micro | Tecla |
| --- | ---: | --- |
| 1 | 2 | F13 |
| 2 | 3 | F14 |
| 3 | 4 | F15 |
| 4 | 5 | F16 |
| 5 | 6 | F17 |
| 6 | 7 | F18 |

Cada botón va entre su pin y `GND`. El firmware usa `INPUT_PULLUP`.

## Ejecutar en Windows durante desarrollo

```bat
launch_desktop.bat
```

## Generar instalador Windows

En la máquina de desarrollo:

```bat
build_release_winteros.bat
```

El instalador final queda en:

```text
release\SATURN-Control-Setup-1.0.0.exe
```

El usuario final solo necesita ese archivo. No necesita Python, pip, PyInstaller ni Inno Setup.

## Ejecutar en Linux

```bash
chmod +x launch_linux.sh
./launch_linux.sh
```

Ver más en [README_LINUX.md](README_LINUX.md).

## Documentación

- [CHANGELOG.md](CHANGELOG.md)
- [ROADMAP.md](ROADMAP.md)
- [AUTHORSHIP.md](AUTHORSHIP.md)
- [README_WINDOWS_EXE.md](README_WINDOWS_EXE.md)
- [README_DISTRIBUCION.md](README_DISTRIBUCION.md)
- [firmware/README.md](firmware/README.md)

## Marca y autoría

Proyecto creado por **Francisco Duarte** bajo la marca personal/laboratorio **FD Labs**.

SATURN Control, su código, firmware, diseño y documentación se publican como registro de desarrollo y portfolio. Ver [LICENSE](LICENSE).

## Nota

Este proyecto está en evolución. La versión 1.0.0 representa una primera base funcional y distribuible, no el final del producto.
