# SATURN Control como .exe

Este proyecto puede empaquetarse en Windows con PyInstaller.

## Requisitos

- Windows 10/11.
- Python 3 instalado desde python.org.
- Marcar `Add Python to PATH` durante la instalación.

## Usar tu propia foto como icono

Guardá tu imagen en:

```text
assets\icon_source.png
```

También sirve:

```text
assets\icon_source.jpg
assets\icon_source.jpeg
assets\icon_source.webp
```

Cuando ejecutes `build_windows.bat`, esa imagen se convierte automáticamente en:

```text
assets\saturn_icon.ico
```

Ese `.ico` se usa en el `.exe` y en el instalador. Para que quede bien, conviene que la imagen sea cuadrada o tenga el logo centrado.

## Crear el ejecutable

Antes de compilar, podés probar la ventana de escritorio con:

```bat
launch_desktop.bat
```

Desde la carpeta del proyecto, ejecutá:

```bat
build_windows.bat
```

El script genera:

```text
dist\SATURN-Control.exe
dist\SATURN-Control-Debug.exe
```

Esos archivos quedan dentro de la carpeta del proyecto, en `dist`.

`SATURN-Control.exe` abre una ventana propia de escritorio con la web integrada.
No necesita abrir Chrome, Edge o Firefox como pestaña externa.

## Cuál usar

- `SATURN-Control.exe`: versión normal, sin consola.
- `SATURN-Control-Debug.exe`: versión con consola para diagnosticar errores.

Si la versión normal no abre o no detecta teclas, probá primero la versión Debug para ver mensajes.

## Dónde se guarda la configuración

Cuando corre como `.exe`, SATURN guarda `config.json` en:

```text
%APPDATA%\SATURN Control\config.json
```

Ejemplo:

```text
C:\Users\TuUsuario\AppData\Roaming\SATURN Control\config.json
```

Si borrás ese archivo, SATURN crea una copia nueva desde la configuración incluida en el ejecutable.

## Crear instalador con icono en escritorio

Opcionalmente podés crear un instalador con Inno Setup. Esta es la forma más prolija para compartir SATURN con otra persona.

1. Instalá Inno Setup 6.
2. Ejecutá:

```bat
build_installer_windows.bat
```

Eso genera:

```text
installer_output\SATURN-Control-Setup-1.0.0.exe
```

Ese instalador:

- Pide permisos de administrador con UAC.
- Instala SATURN en `C:\Program Files\SATURN Control`.
- Crea acceso directo en escritorio si el usuario lo marca.
- Crea acceso en menú inicio.
- Permite activar inicio automático con Windows.
- Incluye desinstalador desde Configuración > Aplicaciones.

La app instalada abre sin consola. La consola queda solo para `SATURN-Control-Debug.exe`, que sirve para diagnosticar errores.

## Crear release final

Para generar el archivo final que compartirías con otra persona, ejecutá:

```bat
build_release_winteros.bat
```

Eso deja el entregable en:

```text
release\SATURN-Control-Setup-1.0.0.exe
```

Ese es el archivo para usuarios. No hace falta compartir `.bat`, Python, dependencias ni carpetas internas.

## Notas

- La primera vez Windows Defender puede tardar un poco en analizar el `.exe`.
- Si Windows SmartScreen avisa que es una app desconocida, es normal en ejecutables propios sin firma digital.
- Para distribuirlo de forma más profesional después conviene agregar instalador y firma digital.
