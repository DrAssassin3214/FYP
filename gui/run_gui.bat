@echo off
rem Start the masonry delay-risk decision-support GUI (local only, offline).
rem Double-click this file, or run it from a terminal. Close with Ctrl+C.
cd /d "%~dp0.."
python -m gui %*
if errorlevel 1 (
  echo.
  echo The GUI stopped with an error. Check that Python 3 and Flask are installed:
  echo     python -m pip install flask
  pause
)
