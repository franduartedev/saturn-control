@echo off
title SATURN Stream Deck
color 0B
cd /d "%~dp0"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

cls
echo.
echo  ==========================================
echo             SATURN Stream Deck
echo  ==========================================
echo.
echo  Iniciando el panel de macros...
echo  No cierres esta ventana mientras uses SATURN.
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

if not exist ".venv\Scripts\python.exe" (
  echo  Preparando entorno por primera vez...
  %PY_CMD% -m venv .venv
)

call ".venv\Scripts\activate.bat"

echo  Revisando dependencias...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

cls
echo.
echo  ==========================================
echo             SATURN esta listo
echo  ==========================================
echo.
echo  Panel web: http://localhost:5000
echo.
echo  Se abrira en tu navegador automaticamente.
echo  Para cerrar SATURN, volve a esta ventana y presiona CTRL+C.
echo.
python app.py
echo.
echo  SATURN se cerro.
pause
