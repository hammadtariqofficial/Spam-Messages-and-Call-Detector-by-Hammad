# Changelog

## 1.0.1-INDUSTRIAL-HARDENED — 2026-09-04

- Hardened Windows/PyInstaller resource and writable-data handling.
- Added safer per-user history storage and diagnostics logging.
- Improved spam/scam rule combinations and explainable reasons.
- Added benign hard-negative contexts to reduce false positives.
- Added input normalization and safety limits.
- Hardened optional live-call/audio behavior for missing dependencies/devices.
- Added reproducible ML dataset/training pipeline and holdout evaluation.
- Added 160 deterministic end-to-end regression tests.
- Added model card, technical specification, release checklist and QA report.
- Updated README and release documentation.
- Repository hygiene improved so local environments, databases, logs and build artifacts are not committed.

### Validation

- Holdout test accuracy: 99.73%
- Spam precision: 99.35%
- Spam recall: 100%
- Regression tests: 160/160 passed

> Metrics are engineering validation on the supplied expanded dataset, which contains synthetic/template-generated examples. They are not a guarantee of production accuracy.
