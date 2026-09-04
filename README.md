# Spam Message & Call Detector — Industrial Edition

A Windows desktop spam/scam risk detector for SMS and call-related text analysis.

## Project 7 coverage

- Normal / Suspicious / Spam classification
- SMS and call-related text analysis
- Pattern and rule analysis
- Suspicious link detection
- Urgency / pressure detection
- Repeated promotional language detection
- Sensitive information / OTP / password detection
- Optional unknown/private sender context
- ML classification using TF-IDF + Logistic Regression
- Explainable detection reasons
- Risk score + severity
- Safety recommendation
- Scan history and audit database
- Dashboard and result visualization
- JSON/TXT result export
- Consent-based live speech-to-text analysis when compatible audio/STT dependencies are installed
- One-file Windows EXE build with PyInstaller

## Industrial hardening

Version: **1.0.1-INDUSTRIAL-HARDENED**

The hardened release adds safer Windows resource handling, writable per-user history storage, graceful missing-audio dependency handling, input limits, improved false-positive handling, strong scam-combination rules, benign hard-negative contexts, reproducible ML training, automated regression tests, and release/QA documentation.

## ML pipeline

- `training/build_dataset.py` — reproducibly builds the expanded labelled dataset.
- `training/train_model.py` — grouped train/validation/test split, word + character TF-IDF, Logistic Regression, metrics and model export.
- `tests/test_detector_160.py` — 160 deterministic end-to-end regression cases.
- `reports/ml_evaluation.json` — evaluation metrics.
- `reports/automated_test_report.json` — automated test results.

Latest engineering validation:

- Test accuracy: **99.73%**
- Spam precision: **99.35%**
- Spam recall: **100%**
- Holdout test size: **374**
- Regression suite: **160/160 passed**

> The expanded dataset contains synthetic/template-generated examples. These metrics are engineering validation, not a guarantee of real-world production accuracy. A production deployment needs a large, independently collected and legally usable benchmark dataset plus drift monitoring.

## Run from source

On Windows, use `RUN_SOURCE.bat`.

## Build one Windows EXE

On a Windows 10/11 x64 build PC, double-click `BUILD_ONE_EXE.bat`.

The build performs syntax checks, model training, final verification, smoke tests and the 160-case regression suite before creating the PyInstaller one-file executable.

Output:

`dist\\SpamMessageCallDetector.exe`

The end user does not need Python, pip, scikit-learn or the source tree to run the packaged EXE.

## Live Call note

The Live Call tab performs consent-based audio capture and speech-to-text analysis. It does **not** intercept cellular/SIM calls and does not save raw audio. External speech recognition may require internet access depending on the configured recognizer.

## Safety

The detector is a defensive advisory classifier. A risk score is not proof that a message is malicious. Never disclose OTPs/passwords or send money based only on a message or caller request. Verify important requests through an independently obtained official channel.
