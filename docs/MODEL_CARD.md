# Model Card — Spam Message & Call Detector

## Model
Word + character TF-IDF features with Logistic Regression. The detector combines ML probability with explainable rule indicators to produce an advisory 0–100 risk score.

## Intended use
Defensive screening of SMS/call-related text for Normal, Suspicious, or Spam classification. It is an advisory tool and must not be treated as proof of malicious intent.

## Training data
The current release contains 1,930 labelled rows: 920 spam and 1,010 normal. It combines curated baseline examples with synthetic/template-generated examples and hard negatives.

## Evaluation
Grouped holdout test: 374 rows. Accuracy 99.73%, spam precision 99.35%, spam recall 100%, spam F1 99.67%. Because synthetic/template-generated data is included, these numbers are engineering validation metrics, not evidence of production accuracy.

## Limitations
- Real-world distribution shift can reduce performance.
- Dataset is not a substitute for independently collected production data.
- Rule indicators can affect risk independently of ML probability.
- Live call mode analyzes PC microphone/system audio; it does not intercept cellular/SIM calls.
- Live transcription may use an external speech-recognition service when enabled.

## Recommended production validation
Evaluate on a legally usable, independently collected dataset with temporal separation, language diversity, scam-family diversity, calibration analysis, precision/recall/F1, false-positive/false-negative rates, and drift monitoring.
