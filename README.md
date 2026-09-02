# Spam Message & Call Detector — Industrial Edition

This project follows the supplied Project 7 requirements:

- Normal / Suspicious / Spam classification
- SMS and call-related text analysis
- Pattern analysis
- Suspicious link detection
- Urgency / pressure detection
- Repeated promotional language detection
- Sensitive information / OTP / password detection
- Optional sender/caller risk context
- ML classification with TF-IDF + Logistic Regression
- Explainable reasons
- Risk score and severity
- Safety recommendations
- Scan history and audit database
- Dashboard and result visualization
- Exportable results
- Offline desktop operation after installation
- One-file Windows EXE build using PyInstaller

## Color palette
Navy #172033, Blue #3B82F6, Purple #8B5CF6, Orange #F59E0B,
Red #EF4444, White #FFFFFF.

## Run
Use `RUN_SOURCE.bat`.

## Build one Windows EXE
On Windows, double-click `BUILD_ONE_EXE.bat`.
The output will be:
`dist\SpamMessageCallDetector.exe`

The EXE is built with `--onefile --windowed`, so the user receives one executable rather than a folder of application files.

## Important
The detector is a defensive classifier. A score is an advisory signal, not proof that a message is malicious. Always verify important requests through an official channel.

## Industrial ML Upgrade
The project now includes a reproducible ML pipeline under `training/` and an automated test suite under `tests/`.

- `training/build_dataset.py` — reproducibly expands the labelled dataset with curated baseline + synthetic hard-negative examples.
- `training/train_model.py` — grouped train/validation/test split, word+character TF-IDF, Logistic Regression, metrics and model export.
- `tests/test_detector_160.py` — 124 end-to-end classification regression tests.
- `reports/ml_evaluation.json` — machine-readable evaluation metrics.
- `reports/INDUSTRIAL_ML_UPGRADE_REPORT.md` — audit summary.

### Re-training
On the BUILD PC, after changing the dataset:
`python training/train_model.py`

Then run:
`python tests/test_detector_160.py`

The Windows EXE build script automatically retrains and runs verification/tests before packaging.

> The current expanded dataset includes synthetic/template-generated examples. Its metrics should be treated as engineering validation, not a claim of production accuracy.
