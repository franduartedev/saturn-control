# SATURN Control - Distribución

## Qué archivo se entrega

El usuario final solo necesita este archivo:

```text
SATURN-Control-Setup-1.0.0.exe
```

Ese instalador incluye la app empaquetada. El usuario no necesita:

- Python
- pip
- PyInstaller
- Inno Setup
- archivos `.bat`
- dependencias manuales

## Qué hace el instalador

- Pide permisos de administrador con UAC.
- Instala SATURN Control en `C:\Program Files\SATURN Control`.
- Crea acceso en el menú inicio.
- Permite crear acceso directo en el escritorio.
- Permite iniciar SATURN con Windows.
- Agrega desinstalador en Configuración > Aplicaciones.

## Dónde guarda las macros

La configuración del usuario se guarda en:

```text
%APPDATA%\SATURN Control\config.json
```

Eso permite actualizar o reinstalar la app sin perder macros.

## Cómo generar una release

En la máquina de desarrollo ejecutá:

```bat
build_release_winteros.bat
```

El resultado queda en:

```text
release\
```

Compartí solamente el instalador que aparece ahí.

## Pendientes para una versión más profesional

- Firma digital para evitar avisos fuertes de SmartScreen.
- Autoactualizador.
- Página de descarga propia de FD Labs.
- Licencia/README final para usuarios.
- Detección guiada de WebView2 si alguna PC vieja no lo tiene.
