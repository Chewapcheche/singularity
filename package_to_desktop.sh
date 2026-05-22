#!/usr/bin/env bash
# Copy game to ~/Desktop/PokemonDotaTD (Linux/macOS)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DESKTOP="${HOME}/Desktop/PokemonDotaTD"
mkdir -p "$DESKTOP"

echo "Copying to $DESKTOP ..."
cp -r "$ROOT/game" "$DESKTOP/"
cp "$ROOT/main.py" "$ROOT/requirements.txt" "$ROOT/README.md" "$ROOT/LAUNCH.txt" "$DESKTOP/"
cp "$ROOT/build_windows.bat" "$ROOT/package_to_desktop.bat" "$DESKTOP/" 2>/dev/null || true
cp "$ROOT/run_game.sh" "$ROOT/build_linux.sh" "$DESKTOP/" 2>/dev/null || true

if [[ -f "$ROOT/dist/PokemonDotaTD" ]]; then
  cp "$ROOT/dist/PokemonDotaTD" "$DESKTOP/PokemonDotaTD"
  chmod +x "$DESKTOP/PokemonDotaTD"
fi

echo "Done: $DESKTOP"
