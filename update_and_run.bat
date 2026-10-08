@echo off
rem Brings this folder up to date with GitHub (DrAssassin3214/FYP, branch main), installs the requirements
rem and starts the GUI.  Works in a plain folder as well as in a git clone.  Your own untracked files
rem (research papers, .docx, .xlsx, literature database) are NOT touched; files that are in the repository
rem are replaced by the latest version.  Needs Git (https://git-scm.com) and Python 3 on PATH; GitHub will
rem ask you to sign in the first time because the repository is private.
cd /d "%~dp0"
where git >nul 2>nul
if errorlevel 1 (
  echo Git was not found. Install it from https://git-scm.com/download/win and run this file again.
  pause
  exit /b 1
)
if not exist .git (
  git init -b main
  git remote add origin https://github.com/DrAssassin3214/FYP.git
)
git fetch origin main
if errorlevel 1 (
  echo Could not reach GitHub. Check your internet connection and sign-in, then run this file again.
  pause
  exit /b 1
)
git checkout -f -B main origin/main
if errorlevel 1 (
  echo Update failed.
  pause
  exit /b 1
)
if not exist .venv (
  python -m venv .venv
  if errorlevel 1 (
    echo Python 3 was not found. Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
    pause
    exit /b 1
  )
)
call .venv\Scripts\activate.bat
python -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo Package install failed. Check your internet connection and try again.
  pause
  exit /b 1
)
python -m gui
pause
