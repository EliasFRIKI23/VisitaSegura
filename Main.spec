# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Obtener rutas de las librerías
venv_path = Path(sys.prefix)
site_packages = venv_path / 'Lib' / 'site-packages'

# Buscar librerías de zbar y opencv
zbar_path = site_packages / 'pyzbar'
opencv_path = site_packages / 'cv2'

# Binarios adicionales para incluir
binaries_to_add = []

# Agregar DLLs de zbar si existen
if zbar_path.exists():
    for dll in zbar_path.rglob('*.dll'):
        binaries_to_add.append((str(dll), 'pyzbar'))

# Agregar DLLs de opencv si existen
if opencv_path.exists():
    for dll in opencv_path.rglob('*.dll'):
        binaries_to_add.append((str(dll), 'cv2'))

# Datos adicionales (logo, etc)
datas_to_add = []
if os.path.exists('Logo Duoc .png'):
    datas_to_add.append(('Logo Duoc .png', '.'))

a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=binaries_to_add,
    datas=datas_to_add,
    hiddenimports=[
        'cv2',
        'pyzbar',
        'pyzbar.pyzbar',
        'numpy',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'pymongo',
        'pandas',
        'openpyxl',
        'reportlab',
        'matplotlib',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.figure',
        'matplotlib.dates',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='VisitaSegura',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
