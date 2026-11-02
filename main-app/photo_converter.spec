# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Photo Converter (Linux / Windows / macOS)."""

from __future__ import annotations

import platform
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None
ROOT = Path(SPECPATH)  # noqa: F821 — injected by PyInstaller

datas = [
    (str(ROOT / "assets" / "icon.png"), "assets"),
    (str(ROOT / "assets" / "icon.ico"), "assets"),
]
datas += collect_data_files("customtkinter")

binaries = []
hiddenimports = [
    "PIL._tkinter_finder",
    "pillow_heif",
    "customtkinter",
    "darkdetect",
]

# Pull pillow-heif native bits when present.
try:
    tmp_ret = collect_all("pillow_heif")
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]
except Exception:
    pass

system = platform.system().lower()
icon_file = None
if system == "windows":
    icon_file = str(ROOT / "assets" / "icon.ico")
elif system == "darwin":
    # .icns optional; PNG fallback is fine for many setups.
    icns = ROOT / "assets" / "icon.icns"
    icon_file = str(icns) if icns.exists() else str(ROOT / "assets" / "icon.png")
else:
    icon_file = str(ROOT / "assets" / "icon.png")

a = Analysis(  # noqa: F821
    [str(ROOT / "run.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="PhotoConverter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app — no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)
