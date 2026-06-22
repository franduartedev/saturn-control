# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules


block_cipher = None

hiddenimports = [
    "engineio.async_drivers.threading",
    "keyboard",
    "pyautogui",
    "webview",
    "obsws_python",
    "comtypes",
    "pycaw",
    "pycaw.pycaw",
] + collect_submodules("flask_socketio") + collect_submodules("webview")

datas = [
    ("web", "web"),
    ("config.json", "."),
    ("firmware", "firmware"),
    ("assets", "assets"),
    ("README_WINDOWS_EXE.md", "."),
    ("README_LINUX.md", "."),
]

a = Analysis(
    ["desktop_app.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pynput"],
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
    name="SATURN-Control",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    icon="assets/saturn_icon.ico",
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
