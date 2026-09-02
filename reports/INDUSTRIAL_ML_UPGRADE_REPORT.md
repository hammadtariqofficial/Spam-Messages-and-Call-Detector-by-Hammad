# Industrial ML Upgrade Report

## Scope
This release upgrades the detector from a small demonstration model to a reproducible ML training/evaluation workflow.

## Dataset
- 1,930 labelled message rows
- 920 spam / 1,010 normal
- Original curated examples preserved in `data/spam_dataset_original.csv`
- Additional hard-negative normal examples cover benign security, finance, delivery, account and education language.
- Dataset generation is reproducible with `training/build_dataset.py`.

## Training pipeline
`training/train_model.py` performs:
1. CSV loading and label normalization
2. Grouped train/validation/test splitting to reduce template leakage
3. Word-level TF-IDF features with 1-2 grams
4. Character TF-IDF features with 3-5 character windows
5. Logistic Regression with balanced class weighting
6. Validation metrics
7. Final fit on train + validation data
8. Model export to `models/spam_model.pkl`
9. Evaluation report export to `reports/ml_evaluation.json` and `.txt`

## Evaluation
Current grouped holdout test result:
- Accuracy: **99.73%**
- Spam precision: **99.35%**
- Spam recall: **100%**
- Spam F1: **99.67%**
- Test size: **374**
- Confusion matrix (normal, spam): `[[220, 1], [0, 153]]`

Validation:
- Accuracy: **99.69%**
- Spam precision: **99.37%**
- Spam recall: **100%**
- Spam F1: **99.68%**

## Automated end-to-end tests
`tests/test_detector_160.py` currently executes **124 deterministic cases** across Normal, Spam and Suspicious classes, including unknown-sender scenarios and benign hard negatives.

Latest result:
- **124 / 124 passed**
- **100% pass rate**

## Important production caveat
The expanded dataset contains synthetic/template-generated examples in addition to the original curated examples. Therefore the reported metrics are **engineering validation metrics**, not proof of real-world production accuracy. A commercial deployment should retrain/evaluate against a large, independently collected and legally usable real-world dataset and monitor drift over time.
