# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all


streamlit_datas, streamlit_binaries, streamlit_hiddenimports = collect_all(
    "streamlit"
)

datas = [
    ("dashboard.py", "."),
    ("painel.py", "."),
    ("VERSION", "."),
]

datas += streamlit_datas

hiddenimports = [
    "data_service",
    "analytics_view",
    "data_manager",
    "data_install",
    "signals",
    "baixar_dados",
    "baixar_logs",
    "download_tse",
    "analise",
    "paths",
    "version",
    "logs_urna",
]

hiddenimports += streamlit_hiddenimports


a = Analysis(
    ["launcher.py"],
    pathex=[],
    binaries=streamlit_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name="ESTELEICAO",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ESTELEICAO",
)
