#!/usr/bin/env python3
"""
Pokemon vs Dota TD — offline desktop tower defense.
Run: python main.py
"""

from __future__ import annotations

import atexit
import os
import sys

if not os.environ.get("DISPLAY"):
    os.environ.setdefault("DISPLAY", ":0")

from ursina import Ursina, application, window  # noqa: E402

from game.app import TDGame  # noqa: E402

app = Ursina(
    title="Pokemon vs Dota TD",
    borderless=False,
    fullscreen=False,
    development_mode=False,
    vsync=True,
    audio=False,
)
window.size = (1280, 720)
window.exit_button.visible = True
window.fps_counter.enabled = True

game = TDGame(app)
atexit.register(game.shutdown)
window.exit_button.on_click = game.shutdown


def update():
    if not game._shutting_down:
        game.update()


def input(key):
    if not game._shutting_down:
        game.input(key)


def main():
    try:
        app.run()
    except SystemExit:
        raise
    except Exception:
        game.shutdown()
        raise
    finally:
        if not game._shutting_down:
            game.shutdown()


if __name__ == "__main__":
    main()
