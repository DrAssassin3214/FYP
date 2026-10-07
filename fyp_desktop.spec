# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the PySide6 desktop app.  Build with:  pyinstaller fyp_desktop.spec --noconfirm
from PyInstaller.utils.hooks import collect_submodules

datas = [
    ("data", "data"),
    ("Research_Notes", "Research_Notes"),
    ("Literature_Evidence_Package.xlsx", "."),
    ("gui/static", "gui/static"),
]

a = Analysis(
    ["fyp_desktop.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=collect_submodules("app") + collect_submodules("gui")
    + ["PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["pytest", "pandas", "statsmodels", "docx", "tkinter", "IPython", "notebook"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FYP-Risk-Tool-Desktop",
    debug=False,
    strip=False,
    upx=False,
    console=False,      # a normal desktop program: no console window
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="FYP-Risk-Tool-Desktop",
)
