# -*- mode: python ; coding: utf-8 -*-

import os

# Agregar archivos .ico como datos
ico_dir = os.path.join('img', 'iconos')
ico_files = [(os.path.join(ico_dir, f), os.path.join(ico_dir)) for f in os.listdir(ico_dir) if f.endswith('.ico')]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=ico_files,  # <-- Aquí se añaden los íconos
    hiddenimports=[],
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
    name='cal-cucho',
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
    icon='img/iconos/inicio2.ico',  # Usa una ruta relativa para evitar errores
)
