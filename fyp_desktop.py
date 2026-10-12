"""Entry point for the PySide6 desktop app (also used to build the Windows .exe)."""
import sys

from gui.qt_app import main

if __name__ == "__main__":
    sys.exit(main())
