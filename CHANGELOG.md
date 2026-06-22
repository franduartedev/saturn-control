# Changelog

## 1.0.0 - 2026-06-23

Primera versión estable de SATURN Control.

### Agregado

- Panel de control visual para macro deck casero.
- UI local estilo SATURN/FD Labs con modo app de escritorio.
- Soporte para Arduino Pro Micro como teclado HID.
- Firmware para 6 botones físicos usando `F13` a `F18`.
- Diagnóstico de teclas detectadas.
- Configuración de macros desde la interfaz web.
- Perfiles de macros.
- Acciones para multimedia, sistema, apps, web, OBS, VS Code y comandos personalizados.
- Build Windows con PyInstaller.
- Instalador Windows con Inno Setup.
- Icono personalizable desde imagen.
- Scripts Linux para ejecución y autoinicio.

### Notas

- La configuración del usuario en Windows se guarda en `%APPDATA%\SATURN Control\config.json`.
- El instalador final se genera en `release\SATURN-Control-Setup-1.0.0.exe`.
