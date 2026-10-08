@echo off
rem Start the masonry delay-risk decision-support GUI (local only, offline).
rem Double-click this file, or run it from a terminal. Close with Ctrl+C.
rem If this folder is a git clone, it is brought up to date first (skipped silently when offline).
cd /d "%~dp0.."
if exist .git (
  git pull --ff-only >nul 2>nul
)
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe -m gui %*
) else (
  python -m gui %*
)
if errorlevel 1 (
  echo.
  echo The GUI stopped with an error. Check that Python 3 and Flask are installed:
  echo     python -m pip install -r requirements.txt
  pause
)
