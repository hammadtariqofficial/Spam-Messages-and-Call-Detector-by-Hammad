# PyInstaller Warning Fix QA — 2.1.1

## Root cause
The Windows builder recursively collected large sklearn and google.genai package trees. PyInstaller then attempted to inspect optional test/development modules that are not required at runtime, producing the missing-submodule warnings shown during the build.

## Fix implemented
- Added a focused `SpamMessageCallDetector.spec`.
- Removed broad `collect_submodules sklearn` and `collect_all google.genai` behavior.
- Added explicit runtime hidden imports.
- Excluded optional test/development modules responsible for the reported warnings.
- Updated `BUILD_ONE_EXE.bat` to invoke the focused spec.

## Tests passed in the available environment
- Python compilation: PASS
- Final verification: PASS
- Smoke tests: PASS
- Detector regression: 160/160 PASS
- Edge cases: 20/20 PASS
- Gemini offline test: PASS
- Tkinter UI smoke under Xvfb: PASS
- Hardcoded-secret scan: PASS
- `shell=True` scan: PASS
- TODO/FIXME scan: PASS

## Not tested
- Windows PyInstaller compilation: NOT TESTED — Windows runtime is required.
- Final Windows EXE launch: WINDOWS REQUIRED.
- Real microphone/system-loopback capture: WINDOWS HARDWARE REQUIRED.
