# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

root = Path(SPECPATH).resolve()

a = Analysis(
    [str(root / "main.py")],
    pathex=[str(root)],
    binaries=[],
    datas=[
        (str(root / "assets" / "logo.png"), "assets"),
        (str(root / "assets" / "logo.ico"), "assets"),
    ],
    hiddenimports=sorted(collect_submodules("yt_dlp")),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "fastapi",
        "httpx",
        "httpcore",
        "opentelemetry",
        "pydantic",
        "uvicorn",
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="gdrive-dl-gui",
    icon=str(root / "assets" / "logo.ico"),
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
)
