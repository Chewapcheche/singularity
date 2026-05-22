@echo off
setlocal
cd /d "%~dp0"

set "DESKTOP=%USERPROFILE%\Desktop\PokemonDotaTD"
if not exist "%DESKTOP%" mkdir "%DESKTOP%"

echo Copying game sources to %DESKTOP% ...

xcopy /E /I /Y "game" "%DESKTOP%\game"
copy /Y "main.py" "%DESKTOP%\"
copy /Y "requirements.txt" "%DESKTOP%\"
copy /Y "run_game.sh" "%DESKTOP%\"
copy /Y "README.md" "%DESKTOP%\README.txt"
copy /Y "LAUNCH.txt" "%DESKTOP%\LAUNCH.txt"
copy /Y "build_windows.bat" "%DESKTOP%\build_windows.bat"

if exist "dist\PokemonDotaTD.exe" copy /Y "dist\PokemonDotaTD.exe" "%DESKTOP%\PokemonDotaTD.exe"

echo.
echo Folder ready: %DESKTOP%
echo.
echo To build EXE: open that folder and double-click build_windows.bat
echo Or run game without EXE: pip install -r requirements.txt  then  python main.py
echo.
pause
