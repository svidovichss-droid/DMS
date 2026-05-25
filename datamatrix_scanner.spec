# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for DataMatrix Quality Scanner
Build command: pyinstaller datamatrix_scanner.spec --clean
"""

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect all dependencies for key packages
opencv_data = collect_all('cv2')
numpy_data = collect_all('numpy')
pil_data = collect_all('PIL')
customtkinter_data = collect_all('customtkinter')
pyzbar_data = collect_all('pyzbar')

# Build hidden imports list
hiddenimports = []
hiddenimports += collect_submodules('cv2')
hiddenimports += collect_submodules('numpy')
hiddenimports += collect_submodules('PIL')
hiddenimports += collect_submodules('customtkinter')
hiddenimports += collect_submodules('pyzbar')
hiddenimports += [
    'pkg_resources.py2_warn',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json.example', '.'),
        ('resources', 'resources'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
    ],
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
    name='DataMatrixScanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Set to 'resources/icon.ico' when you have a valid icon file
)