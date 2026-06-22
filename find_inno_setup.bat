@echo off
title Buscar Inno Setup
color 0B

echo.
echo  ==========================================
echo            Buscando Inno Setup
echo  ==========================================
echo.

set "FOUND="

where ISCC.exe >nul 2>nul
if %errorlevel%==0 (
  for /f "delims=" %%I in ('where ISCC.exe') do (
    echo  Encontrado en PATH:
    echo    %%I
    set "FOUND=1"
  )
)

for %%P in (
  "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
  "%ProgramFiles%\Inno Setup 6\ISCC.exe"
  "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
  "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"
  "%ProgramFiles%\Inno Setup 7\ISCC.exe"
  "%LocalAppData%\Programs\Inno Setup 7\ISCC.exe"
) do (
  if exist %%~P (
    echo  Encontrado:
    echo    %%~P
    set "FOUND=1"
  )
)

echo.
echo  Busqueda amplia en Program Files, puede tardar unos segundos...
for /f "delims=" %%I in ('where /r "%ProgramFiles(x86)%" ISCC.exe 2^>nul') do (
  echo  Encontrado:
  echo    %%I
  set "FOUND=1"
)

for /f "delims=" %%I in ('where /r "%ProgramFiles%" ISCC.exe 2^>nul') do (
  echo  Encontrado:
  echo    %%I
  set "FOUND=1"
)

if not defined FOUND (
  echo  No encontre ISCC.exe.
  echo.
  echo  Reinstala Inno Setup 6 y asegurate de que termine correctamente.
)

echo.
pause
