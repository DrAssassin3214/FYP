@echo off
rem Builds the Windows program:  dist\FYP-Risk-Tool\FYP-Risk-Tool.exe
rem Needs Python 3.10 - 3.13 on PATH and an internet connection (first run only).
cd /d "%~dp0"
if not exist .venv-build (
  python -m venv .venv-build
  if errorlevel 1 (
    echo Python 3 was not found. Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
    pause
    exit /b 1
  )
)
call .venv-build\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
  echo Package install failed. Check your internet connection and try again.
  pause
  exit /b 1
)
pyinstaller fyp_gui.spec --noconfirm --clean
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)
echo.
echo Done. Run dist\FYP-Risk-Tool\FYP-Risk-Tool.exe  (copy the whole FYP-Risk-Tool folder to move it).
pause
