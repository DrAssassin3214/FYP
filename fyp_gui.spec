# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the offline FYP risk tool.  Build with:  pyinstaller fyp_gui.spec --noconfirm
#
# The app locates its files relative to the package folders (Path(__file__).parents[1]), so the data
# is bundled at the SAME relative layout it has in the repository.
from PyInstaller.utils.hooks import collect_submodules

datas = [
    ("data", "data"),
    ("Research_Notes", "Research_Notes"),
    ("Literature_Evidence_Package.xlsx", "."),
    ("gui/static", "gui/static"),
]

a = Analysis(
    ["fyp_gui.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=collect_submodules("app") + collect_submodules("gui"),
    hookspath=[],
    runtime_hooks=[],
    # Only needed by the research scripts / tests, not by the GUI.
    excludes=["pytest", "pandas", "statsmodels", "docx", "tkinter", "IPython", "notebook"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FYP-Risk-Tool",
    debug=False,
    strip=False,
    upx=False,
    console=True,       # keep the console: it shows the address and Ctrl+C stops the server
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="FYP-Risk-Tool",
)
