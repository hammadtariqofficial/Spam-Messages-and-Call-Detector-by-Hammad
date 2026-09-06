# Windows EXE Build

## Clean build

Run `BUILD_ONE_EXE.bat` on Windows 10/11 x64 with Python 3.11–3.13 installed.

The script creates an isolated `.venv`, installs `requirements.txt`, runs the regression/smoke checks, and invokes `SpamMessageCallDetector.spec`.

Output:

`release\Spam Messages and Call Detector.exe`

## PyInstaller warning fix

The previous builder recursively collected all sklearn and google.genai submodules. That caused optional-module warnings for modules such as `sklearn.external.array_api_compat.torch`, `google.genai.tests`, `pytest`, `pycparser`, `tzdata`, and `scipy.special._cdflib`.

The new spec uses an explicit runtime import list and excludes optional test/development modules. It does not recursively collect the entire sklearn or google.genai package trees.

## Gemini

Gemini is optional. Do not place API keys in source code or the EXE. Configure `GEMINI_API_KEY` using `CONFIGURE_GEMINI.bat` or the Windows environment.

## Windows-only validation

The actual EXE must be launched on Windows after packaging. Microphone and system-loopback capture also require Windows hardware/runtime validation.
