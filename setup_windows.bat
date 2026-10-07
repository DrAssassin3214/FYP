@echo off
rem One-time setup on Windows: creates a virtual environment, installs the requirements and starts the GUI.
rem Double-click this file. Afterwards you can start the GUI with gui\run_gui.bat or "python -m gui".
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
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Package install failed. Check your internet connection and try again.
  pause
  exit /b 1
)
python -m gui
pause
