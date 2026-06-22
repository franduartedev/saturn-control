@echo off
title SATURN Control - Build Installer WinterOS
color 0B
cd /d "%~dp0"

cls
echo.
echo  ==========================================
echo    SATURN Control - Build Installer Directo
echo  ==========================================
echo.

set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"

if not exist "%ISCC%" (
  echo  [ERROR] No encontre Inno Setup en:
  echo    %ISCC%
  echo.
  echo  Ejecuta find_inno_setup.bat para ver donde esta ISCC.exe.
  echo.
  pause
  exit /b 1
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

echo  Generando instalador con:
echo    "%ISCC%"
echo.

"%ISCC%" "installer\SATURN-Control.iss"
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
