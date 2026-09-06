# CHANGELOG

## 2.1.1 — 2026-09-06

### PyInstaller build fix
- Replaced broad `collect_submodules sklearn` and `collect_all google.genai` packaging with a focused `SpamMessageCallDetector.spec`.
- Excluded optional third-party test/development modules that caused the reported missing-submodule warnings.
- Builder now uses the spec directly and writes the final EXE as `Spam Messages and Call Detector.exe`.
- Updated build documentation and project ignore rules.
- Kept Gemini optional and out of source-controlled secrets.

### Validation
- Python compilation: PASS.
- Final verification: PASS.
- Smoke tests: PASS.
- Detector regression: 160/160 PASS.
- Edge cases: 20/20 PASS.
- Gemini offline test: PASS.
- Tkinter UI smoke test under Xvfb: PASS.
- Hardcoded-secret scan: PASS.
- `shell=True` scan: PASS.
- TODO/FIXME scan: PASS.
- Windows PyInstaller build: NOT TESTED — Windows runtime required.

## 1.0.1-INDUSTRIAL-HARDENED — 2026-09-04

### Bugs fixed
- Fixed optional SpeechRecognition/SoundCard initialization so a missing audio stack no longer crashes the desktop application.
- Fixed Windows PC system-audio capture path to resolve loopback microphone sources rather than attempting to record directly from a speaker object.
- Added safer live-device validation and clearer live-mode failure messages.
- Added stronger export error handling for inaccessible/read-only destinations.
- Added vertical and horizontal scrollbars to detection reasons and scan history to prevent UI clipping on smaller windows.
- Corrected detector import ordering and removed an unused CSV import.
- Clarified offline operation: text analysis is offline; external live speech recognition may require internet.

### Validation
- Dataset regeneration: 1,930 labelled rows.
- Grouped holdout test: 374 samples.
- Accuracy: 99.73%.
- Spam precision: 99.35%.
- Spam recall: 100%.
- Spam F1: 99.67%.
- Deterministic detector tests: 160/160 passed.
- Final verification: passed.
- Smoke tests: passed.
- Headless Tkinter GUI smoke test: passed at 1180x760.
- Model loading: passed.
- Optional audio dependencies absent in this Linux environment: application remains usable for text analysis.

### Release note
A native Windows EXE still requires a Windows 10/11 x64 build and runtime smoke test. This Linux environment cannot execute a Windows binary, so the Windows build script is validated but the native EXE runtime itself is not claimed as tested here.
