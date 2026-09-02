# Windows Release / Portability

## Runtime goal
The production artifact is a **single Windows EXE**. End users do not need:
- Python
- pip
- virtualenv
- scikit-learn
- NumPy
- the project source files

The PyInstaller build bundles the application runtime, ML model, vectorizer and required Python packages into the EXE.

## Supported target
The release is designed for **Windows 10/11, 64-bit (x64)**.

A single binary cannot honestly guarantee compatibility with every historical Windows release, Windows ARM build, locked-down corporate policy, missing audio drivers, or third-party antivirus configuration. Those are operating-system/environment constraints rather than application dependencies.

## Build machine
Only the developer/build PC needs Python 3.11–3.13 and internet access to install the build dependencies.

Run:

`BUILD_ONE_EXE.bat`

The script:
1. Creates an isolated build environment.
2. Installs pinned-range dependencies.
3. Runs syntax checks.
4. Runs the detector verification suite.
5. Builds a PyInstaller one-file EXE.
6. Copies the EXE and release notes to `release\`.

## End-user installation
Copy:

`release\SpamMessageCallDetector.exe`

onto the target Windows PC and double-click it. No Python installation is required.

The history database is intentionally stored in the user's LocalAppData area instead of beside the EXE. This prevents write-permission failures when the EXE is placed in protected locations such as Program Files.

## Live Call feature
Live Call is defensive/consent-based audio analysis. It can use a microphone and, where Windows exposes a compatible loopback source, PC system audio. It does not intercept cellular/SIM calls.

Speech-to-text uses the configured Google speech recognition service, so live transcription requires internet access. If audio/STT is unavailable, the main message detector still launches and remains usable.

## First-run checks
For a clean release, test the EXE on a separate Windows 10/11 x64 machine with:
- no Python installed
- no project source folder present
- normal user permissions
- microphone disabled/unavailable
- microphone available
- internet disconnected
- internet connected

The application should still launch and message analysis should remain functional in all of these cases. Live STT should show a friendly status when its external speech service or audio device is unavailable.
