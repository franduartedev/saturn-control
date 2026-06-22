@echo off
title SATURN Control - Build Installer
color 0B
cd /d "%~dp0"

cls
echo.
echo  ==========================================
echo       SATURN Control - Build Installer
echo  ==========================================
echo.

if not exist "assets\saturn_icon.ico" (
  echo  Generando icono SATURN...
  where py >nul 2>nul
  if %errorlevel%==0 (
    set "PY_CMD=py -3"
  ) else (
    set "PY_CMD=python"
  )

  if exist "assets\icon_source.png" (
    %PY_CMD% tools\create_icon_from_image.py
  ) else if exist "assets\icon_source.jpg" (
    %PY_CMD% tools\create_icon_from_image.py
  ) else if exist "assets\icon_source.jpeg" (
    %PY_CMD% tools\create_icon_from_image.py
  ) else if exist "assets\icon_source.webp" (
    %PY_CMD% tools\create_icon_from_image.py
  ) else (
    %PY_CMD% tools\create_saturn_icon.py
  )
)

if not exist "dist\SATURN-Control.exe" (
  echo  No encontre dist\SATURN-Control.exe.
  echo  Voy a generar el ejecutable primero...
  echo.
  call build_windows.bat
  if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] No se pudo generar el ejecutable.
    pause
    exit /b 1
  )
)

set "ISCC="

where ISCC.exe >nul 2>nul
if %errorlevel%==0 (
  set "ISCC=ISCC.exe"
)

if not defined ISCC if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%LocalAppData%\Programs\Inno Setup 7\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 7\ISCC.exe"
if not defined ISCC if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "C:\Program Files\Inno Setup 7\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 7\ISCC.exe"

if not defined ISCC (
  echo  [ERROR] No encontre Inno Setup.
  echo.
  echo  Si ya lo instalaste, cerra esta ventana y abri una terminal nueva.
  echo.
  echo  Tambien podes buscar manualmente ISCC.exe en:
  echo    C:\Program Files\Inno Setup 6\
  echo    C:\Program Files\Inno Setup 7\
  echo.
  pause
  exit /b 1
)

echo  Generando instalador...
echo  Usando Inno Setup:
echo    "%ISCC%"
"%ISCC%" installer\SATURN-Control.iss
if %errorlevel% neq 0 (
  echo.
  echo  [ERROR] Fallo la generacion del instalador.
  pause
  exit /b 1
)

echo.
echo  ==========================================
echo          INSTALADOR TERMINADO
echo  ==========================================
echo.
echo  Archivo:
echo    installer_output\SATURN-Control-Setup-1.0.0.exe
echo.
pause
