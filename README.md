# Spam Messages and Call Detector — Built by Hammad

A Windows desktop application for detecting spam/scam messages and analyzing live call transcripts with a deterministic ML + rule-based engine. Optional Gemini agents provide secondary explanations and safety guidance; they never replace the deterministic classification.

## Features

- Normal / Suspicious / Spam classification
- SMS and call-text analysis
- TF-IDF + Logistic Regression model
- Explainable rule indicators and risk score
- Suspicious URL, urgency, financial, credential/OTP and prize-scam detection
- Optional sender/caller context
- Local SQLite scan history
- Result export
- Consent-based microphone and Windows system-audio loopback analysis
- Optional Gemini AI agent layer
- One-file Windows EXE packaging with PyInstaller

## Run from source

Double-click `RUN_SOURCE.bat` or run:

```text
python spam_detector_desktop.py
```

## Configure Gemini

The Gemini layer is optional. Never commit an API key.

Use `CONFIGURE_GEMINI.bat` or set `GEMINI_API_KEY` in the environment. The application remains fully usable for local deterministic analysis when Gemini is unavailable.

## Build Windows EXE

On Windows 10/11 x64 with Python 3.11–3.13 installed, run:

```text
BUILD_ONE_EXE.bat
```

Output:

```text
release\Spam Messages and Call Detector.exe
```

The build uses `SpamMessageCallDetector.spec`. The previous broad `collect_submodules sklearn` and `collect_all google.genai` approach has been removed because it caused optional-module warnings for packages such as `google.genai.tests`, `pytest`, `pycparser`, `tzdata`, and the sklearn torch compatibility layer.

## QA

The current repair was verified in the available Linux environment with:

- Python compilation: PASS
- Final verification: PASS
- Smoke tests: PASS
- Detector regression: 160/160 PASS
- Edge cases: 20/20 PASS
- Gemini offline behavior: PASS
- Tkinter UI smoke test under Xvfb: PASS
- Hardcoded-secret scan: PASS
- `shell=True` scan: PASS
- TODO/FIXME scan: PASS

The final Windows EXE build and real microphone/system-loopback runtime are Windows-only validations and must be tested on the target Windows PC.

## Project owner

**Built by Hammad**

## Release

**2.1.1 — PyInstaller Warning Fix**
