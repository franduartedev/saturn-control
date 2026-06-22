@echo off
title SATURN Control - Build EXE
color 0B
cd /d "%~dp0"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

cls
echo.
echo  ==========================================
echo          SATURN Control - Build EXE
echo  ==========================================
echo.
echo  Este script genera:
echo    dist\SATURN-Control.exe
echo    dist\SATURN-Control-Debug.exe
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY_CMD=py -3"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PY_CMD=python"
  ) else (
    echo  [ERROR] Python no esta instalado o no esta en PATH.
    echo.
    echo  Instala Python 3 desde python.org y marca "Add Python to PATH".
    pause
    exit /b 1
  )
)

set "VENV_PY=.venv-build\Scripts\python.exe"

if not exist "%VENV_PY%" (
  echo  Preparando entorno de build...
  %PY_CMD% -m venv .venv-build
)

if not exist "%VENV_PY%" (
  echo  [ERROR] No se pudo crear el entorno .venv-build.
  echo.
  echo  Borra la carpeta .venv-build y volve a ejecutar este script.
  pause
  exit /b 1
)

echo  Instalando dependencias de build...
"%VENV_PY%" -m pip install --upgrade pip --quiet
"%VENV_PY%" -m pip install -r requirements-build.txt --quiet

echo.
echo  Generando icono SATURN...
if exist "assets\icon_source.png" (
  "%VENV_PY%" tools\create_icon_from_image.py
) else if exist "assets\icon_source.jpg" (
  "%VENV_PY%" tools\create_icon_from_image.py
) else if exist "assets\icon_source.jpeg" (
  "%VENV_PY%" tools\create_icon_from_image.py
) else if exist "assets\icon_source.webp" (
  "%VENV_PY%" tools\create_icon_from_image.py
) else (
  "%VENV_PY%" tools\create_saturn_icon.py
)
if %errorlevel% neq 0 (
  echo.
  echo  [ERROR] No se pudo generar el icono.
  pause
  exit /b 1
)

echo.
echo  Limpiando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo  Generando EXE normal sin consola...
"%VENV_PY%" -m PyInstaller --clean --noconfirm SATURN-Control.spec
if %errorlevel% neq 0 (
  echo.
  echo  [ERROR] Fallo el build normal.
  pause
  exit /b 1
)

echo.
echo  Generando EXE debug con consola...
"%VENV_PY%" -m PyInstaller --clean --noconfirm SATURN-Control-Debug.spec
if %errorlevel% neq 0 (
  echo.
  echo  [ERROR] Fallo el build debug.
  pause
  exit /b 1
)

echo.
echo  ==========================================
echo             BUILD TERMINADO
echo  ==========================================
echo.
echo  Ejecutable normal:
echo    dist\SATURN-Control.exe
echo.
echo  Ejecutable para diagnostico:
echo    dist\SATURN-Control-Debug.exe
echo.
echo  Recomendacion: probá primero el Debug si algo no abre.
echo.
pause
