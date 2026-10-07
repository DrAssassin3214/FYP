@echo off
rem Start the desktop app from source (creates .venv and installs PySide6 on first run).
cd /d "%~dp0"
if not exist .venv (
  python -m venv .venv
  if errorlevel 1 (
    echo Python 3 was not found. Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
    pause
    exit /b 1
  )
)
call .venv\Scripts\activate.bat
python -m pip install -q -r requirements-desktop.txt
if errorlevel 1 (
  echo Package install failed. Check your internet connection and try again.
  pause
  exit /b 1
)
python -m gui.qt_app
