@echo off
title SATURN Control
color 0B
cd /d "%~dp0"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

cls
echo.
echo  ==========================================
echo              SATURN Control
echo  ==========================================
echo.
echo  Iniciando modo app de escritorio...
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
echo  SATURN se abrira como ventana de escritorio.
echo  Para cerrar todo, cerra la ventana de SATURN.
echo.
python desktop_app.py
