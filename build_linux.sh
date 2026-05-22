#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "=== Pokemon vs Dota TD - Linux build ==="
python3 -m pip install -q -r requirements.txt pyinstaller
python3 -m PyInstaller --noconfirm --clean PokemonDotaTD.spec

DESKTOP="${HOME}/Desktop/PokemonDotaTD"
mkdir -p "$DESKTOP"
cp -f dist/PokemonDotaTD "$DESKTOP/PokemonDotaTD"
chmod +x "$DESKTOP/PokemonDotaTD"
./package_to_desktop.sh

echo "Run: $DESKTOP/PokemonDotaTD"
