@echo off
title SATURN Control - Build Release
color 0B
cd /d "%~dp0"

cls
echo.
echo  ==========================================
echo          SATURN Control - Release
echo  ==========================================
echo.
echo  Este proceso genera el instalador final para usuarios.
echo  El usuario final solo recibe un .exe de instalacion.
echo.

call build_installer_winteros.bat
if %errorlevel% neq 0 (
  echo.
  echo  [ERROR] No se pudo generar el instalador.
  pause
  exit /b 1
)

if not exist "release" mkdir "release"

for %%F in ("installer_output\SATURN-Control-Setup-*.exe") do (
  copy /y "%%~fF" "release\%%~nxF" >nul
)

if exist "README_DISTRIBUCION.md" (
  copy /y "README_DISTRIBUCION.md" "release\README_DISTRIBUCION.md" >nul
)

echo.
echo  ==========================================
echo             RELEASE TERMINADO
echo  ==========================================
echo.
echo  Carpeta final:
echo    release
echo.
echo  Entregable para usuarios:
dir /b "release\SATURN-Control-Setup-*.exe"
echo.
echo  Ese es el archivo que compartis. No compartas los .bat.
echo.
pause
