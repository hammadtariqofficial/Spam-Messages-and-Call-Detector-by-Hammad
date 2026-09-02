@echo off
setlocal
cd /d "%~dp0"
title Spam Message & Call Detector - Source Runner
where py >nul 2>&1
if not errorlevel 1 (set "PY=py -3.12") else (set "PY=python")
if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv
set "VPY=%CD%\.venv\Scripts\python.exe"
"%VPY%" -m pip install -r requirements.txt
if errorlevel 1 goto fail
"%VPY%" spam_detector_desktop.py
exit /b 0
:fail
echo [ERROR] Could not prepare the source environment.
pause
exit /b 1
