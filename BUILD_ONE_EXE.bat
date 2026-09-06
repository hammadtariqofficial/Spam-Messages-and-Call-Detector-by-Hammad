@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Build - Spam Messages and Call Detector

echo ============================================================
echo   SPAM MESSAGE ^& CALL DETECTOR - CLEAN WINDOWS BUILDER
echo ============================================================
echo.

set "PY="
where py >nul 2>&1
if not errorlevel 1 (
  py -3.12 -c "import sys; print(sys.version)" >nul 2>&1
  if not errorlevel 1 set "PY=py -3.12"
)
if not defined PY (
  where python >nul 2>&1
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  echo [ERROR] Python 3.11-3.13 is required on the BUILD PC.
  echo [INFO] The finished EXE does NOT require Python.
  pause
  exit /b 1
)

%PY% -c "import sys; assert (3,11) <= sys.version_info[:2] < (3,14); print('[OK] Python', sys.version)"
if errorlevel 1 goto FAIL

if not exist ".venv\Scripts\python.exe" (
  echo [INFO] Creating isolated build environment...
  %PY% -m venv .venv
  if errorlevel 1 goto FAIL
)
set "VPY=%CD%\.venv\Scripts\python.exe"

"%VPY%" -m pip install --upgrade pip
if errorlevel 1 goto FAIL
"%VPY%" -m pip install -r requirements.txt
if errorlevel 1 goto FAIL

if not exist "models\spam_model.pkl" goto FAIL_MODEL
if not exist "models\tfidf_vectorizer.pkl" goto FAIL_MODEL

"%VPY%" -m py_compile spam_detector_desktop.py detector.py live_call.py ai_agents.py training\train_model.py tests\test_detector_160.py tests\test_edge_cases.py tests\test_ai_agents.py tests\test_ui_smoke.py
if errorlevel 1 goto FAIL

echo [INFO] Running regression and smoke tests...
"%VPY%" final_verification.py
if errorlevel 1 goto FAIL
"%VPY%" smoke_test.py
if errorlevel 1 goto FAIL
"%VPY%" tests\test_detector_160.py
if errorlevel 1 goto FAIL
"%VPY%" tests\test_edge_cases.py
if errorlevel 1 goto FAIL
"%VPY%" tests\test_ai_agents.py
if errorlevel 1 goto FAIL

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist release rmdir /s /q release
mkdir release

echo [INFO] Building with focused PyInstaller spec...
"%VPY%" -m PyInstaller --noconfirm --clean --log-level=ERROR "SpamMessageCallDetector.spec"
if errorlevel 1 goto FAIL

copy /y "dist\Spam Messages and Call Detector.exe" "release\Spam Messages and Call Detector.exe" >nul
copy /y "README.md" "release\README.txt" >nul
if exist "docs\WINDOWS_RELEASE.md" copy /y "docs\WINDOWS_RELEASE.md" "release\WINDOWS_RELEASE.txt" >nul

if not exist "release\Spam Messages and Call Detector.exe" goto FAIL

for %%A in ("release\Spam Messages and Call Detector.exe") do set "SIZE=%%~zA"
echo.
echo ============================================================
echo [SUCCESS] CLEAN WINDOWS ONE-FILE EXE CREATED
echo File: release\Spam Messages and Call Detector.exe
echo Size: %SIZE% bytes
echo.
echo The focused spec excludes optional third-party test/development
necho modules that caused the previous PyInstaller warnings.
echo ============================================================
pause
exit /b 0

:FAIL_MODEL
echo [ERROR] ML model files are missing from models\.
pause
exit /b 1

:FAIL
echo.
echo [ERROR] Release build/verification failed. Fix the message above.
pause
exit /b 1
