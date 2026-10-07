"""Entry point used to build the Windows .exe (PyInstaller). Same as `python -m gui`."""
import sys

from gui.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
