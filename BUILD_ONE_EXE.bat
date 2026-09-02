@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Build - Spam Message & Call Detector

echo ============================================================
echo   SPAM MESSAGE ^& CALL DETECTOR - WINDOWS RELEASE BUILDER
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
  echo [ERROR] Python 3.11-3.13 is required ONLY on the BUILD PC.
  echo [INFO] The finished EXE does NOT require Python.
  pause
  exit /b 1
)

%PY% -c "import sys; assert sys.version_info >= (3,11) and sys.version_info < (3,14); print('[OK] Python', sys.version)"
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

"%VPY%" -m py_compile spam_detector_desktop.py detector.py live_call.py training\train_model.py tests\test_detector_160.py
if errorlevel 1 goto FAIL

echo [INFO] Training industrial ML pipeline...
"%VPY%" training\train_model.py
if errorlevel 1 goto FAIL
"%VPY%" final_verification.py
if errorlevel 1 goto FAIL
"%VPY%" smoke_test.py
if errorlevel 1 goto FAIL
"%VPY%" tests\test_detector_160.py
if errorlevel 1 goto FAIL

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist release rmdir /s /q release
mkdir release

"%VPY%" -m PyInstaller --noconfirm --clean --onefile --windowed --name "SpamMessageCallDetector" --add-data "models;models" --add-data "data;data" --hidden-import=joblib --hidden-import=speech_recognition --hidden-import=soundcard --hidden-import=numpy --hidden-import=sklearn --hidden-import=sklearn.feature_extraction.text --hidden-import=sklearn.linear_model --hidden-import=sklearn.preprocessing --collect-submodules sklearn --collect-data sklearn --collect-all soundcard --collect-all speech_recognition spam_detector_desktop.py
if errorlevel 1 goto FAIL

copy /y "dist\SpamMessageCallDetector.exe" "release\SpamMessageCallDetector.exe" >nul
copy /y "README.md" "release\README.txt" >nul
copy /y "docs\WINDOWS_RELEASE.md" "release\WINDOWS_RELEASE.txt" >nul

if not exist "release\SpamMessageCallDetector.exe" goto FAIL

for %%A in ("release\SpamMessageCallDetector.exe") do set "SIZE=%%~zA"
echo.
echo ============================================================
echo [SUCCESS] WINDOWS ONE-FILE EXE CREATED
echo File: release\SpamMessageCallDetector.exe
echo Size: %SIZE% bytes
echo.
echo Copy ONLY this EXE to a Windows 10/11 x64 PC and run it.
echo Python, pip, sklearn and project files are NOT required.
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
