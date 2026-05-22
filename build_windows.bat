@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo === Pokemon vs Dota TD - Windows build ===
echo.

where py >nul 2>&1 && set PY=py || set PY=python
%PY% --version >nul 2>&1 || (
  echo Python not found. Install from https://www.python.org/ and enable "Add to PATH".
  pause
  exit /b 1
)

echo [1/3] Installing dependencies...
%PY% -m pip install -q -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1

echo [2/3] Building PokemonDotaTD.exe (may take several minutes)...
%PY% -m PyInstaller --noconfirm --clean PokemonDotaTD.spec
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)

echo [3/3] Copying to Desktop\PokemonDotaTD ...
set "DESKTOP=%USERPROFILE%\Desktop\PokemonDotaTD"
if not exist "%DESKTOP%" mkdir "%DESKTOP%"

copy /Y "dist\PokemonDotaTD.exe" "%DESKTOP%\PokemonDotaTD.exe"
copy /Y "README.md" "%DESKTOP%\README.txt"
copy /Y "LAUNCH.txt" "%DESKTOP%\LAUNCH.txt" 2>nul

echo.
echo Done!
echo   Game folder: %DESKTOP%
echo   Run game:    double-click PokemonDotaTD.exe
echo.
pause
