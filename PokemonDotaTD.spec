# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Pokemon vs Dota TD (Windows one-file exe)."""

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None
root = Path(SPECPATH)

datas = []
binaries = []
hiddenimports = collect_submodules("game")

for pkg in ("ursina", "panda3d", "direct", "pandac"):
    try:
        tmp = collect_all(pkg)
        datas += tmp[0]
        binaries += tmp[1]
        hiddenimports += tmp[2]
    except Exception:
        hiddenimports.append(pkg)

hiddenimports += [
    "ursina",
    "ursina.window",
    "ursina.input_handler",
    "panda3d.core",
    "panda3d.direct",
    "direct.showbase",
    "PIL",
    "PIL.Image",
]

a = Analysis(
    [str(root / "main.py")],
    pathex=[str(root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "pandas", "pytest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="PokemonDotaTD",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
