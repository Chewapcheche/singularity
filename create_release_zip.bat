@echo off
setlocal
cd /d "%~dp0"

set "DESKTOP=%USERPROFILE%\Desktop\PokemonDotaTD"
set "ZIP=%USERPROFILE%\Desktop\PokemonDotaTD.zip"

if not exist "%DESKTOP%" (
  echo Run package_to_desktop.bat first.
  pause
  exit /b 1
)

powershell -Command "Compress-Archive -Path '%DESKTOP%\*' -DestinationPath '%ZIP%' -Force"
echo Created: %ZIP%
pause
