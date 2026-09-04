# Project Proposal

## Spam Message & Call Detector
### Industrial-Style Machine Learning and Explainable Threat Detection Platform

**Engineering release:** 1.0.1-INDUSTRIAL-HARDENED

## 1. Executive Summary
The Spam Message & Call Detector is a Windows desktop defensive application that classifies SMS/message text and transcribed call text as **Normal, Suspicious, or Spam**. It combines machine-learning classification with explainable rule indicators, an advisory risk score, sender context, local audit history, safety recommendations, dashboard statistics, result export, and optional consent-based PC-audio transcription.

The release includes a reproducible ML training pipeline, an expanded labelled dataset, grouped train/validation/test evaluation, word- and character-level TF-IDF features, robust input validation, graceful optional-audio failure handling, and 160 deterministic end-to-end regression tests.

## 2. Problem Statement
Users receive phishing, prize, financial, credential, delivery and other socially engineered messages. Manual inspection is inconsistent, while a classifier that only returns a label provides little evidence for the user. The system therefore combines classification with explainable indicators, an advisory risk score and practical safety guidance.

## 3. Aim
To develop a production-oriented **academic prototype** for rapidly screening suspicious message and transcribed call text using machine learning and explainable threat indicators while maintaining a clear Windows desktop interface.

## 4. Objectives
1. Classify text into Normal, Suspicious and Spam categories.
2. Detect indicators including urgency, suspicious links, credential/OTP requests, financial language, prizes, promotions and delivery-related pressure.
3. Combine ML probability and rule evidence into a 0–100 **advisory** risk score.
4. Provide evidence-based reasons and actionable safety recommendations.
5. Maintain local scan history and dashboard statistics.
6. Provide optional consent-based PC microphone/system-audio transcription and analysis.
7. Provide reproducible ML training and evaluation.
8. Validate detector behavior with 160 deterministic regression tests.
9. Provide a Windows one-file EXE build workflow.

## 5. Proposed Methodology
### Data
The current dataset contains **1,930 labelled rows: 920 spam and 1,010 normal**. It combines curated baseline examples, synthetic/template-generated examples, and hard-negative normal examples.

### Machine Learning
The training pipeline uses word-level and character-level TF-IDF features with Logistic Regression and balanced class weighting. Grouped splitting reduces leakage between generated variants. The final model is fitted on training plus validation data while the grouped holdout test set is retained for evaluation.

### Explainable Detection
Rules evaluate urgency, verification, account/security language, financial terms, credentials/OTP, links, rewards/prizes, promotions, investment/loan language, delivery/tracking context and legal pressure. ML probability and rule evidence are fused into an advisory risk score. Context-specific hard negatives reduce obvious false positives in benign educational, office, delivery and academic messages.

### Live Audio Analysis
Optional live mode captures a selected microphone or supported Windows PC-audio loopback source, transcribes short chunks and feeds only the transcript into the same detector. The application does **not** intercept cellular/SIM calls and does not save raw audio. The bundled text detector works offline after installation; the selected external speech-recognition service may require internet access.

## 6. Key Functional Features
- Normal / Suspicious / Spam classification
- 0–100 advisory risk score and severity
- Explainable detection reasons
- Safety recommendations
- Suspicious-link and credential/OTP indicator detection
- Optional sender/caller context
- Local dashboard and scan history
- TXT/JSON result export
- Optional live PC-audio transcription
- Offline text analysis after installation
- One-file Windows EXE build workflow
- Automated ML evaluation and regression testing

## 7. Current Engineering Validation
The grouped holdout test contains **374 samples**. The recorded evaluation is **99.73% accuracy, 99.35% spam precision, 100% spam recall and 99.67% spam F1**. The deterministic regression suite contains **160 cases and passes 160/160**.

These figures are engineering validation only. Because the dataset contains synthetic/template-generated examples, they must not be presented as proof of production accuracy. A production system requires an independently collected, legally usable and temporally separated benchmark with calibration, multilingual coverage, false-positive analysis and drift monitoring.

## 8. Non-Functional Requirements
- Windows 10/11 x64 target
- Responsive desktop interface with scrollable result/history areas
- Input validation and 10,000-character message limit
- Per-user writable audit database
- Graceful handling of missing audio/STT support
- Reproducible model training
- Automated verification before packaging
- No raw-audio persistence

## 9. Limitations
The system is a defensive advisory classifier; a score is not proof of malicious intent. Live mode analyzes PC audio rather than cellular network calls. External speech recognition can require internet access. The current model is English-focused and its dataset is partly synthetic. A Windows-native EXE build must be produced and smoke-tested on an actual Windows 10/11 x64 machine; this development environment cannot execute a Windows binary.

## 10. Future Enhancements
- Large independently collected multilingual dataset
- Probability calibration and threshold optimization
- Local/offline speech-to-text
- Model drift monitoring
- Secure signed updates
- Code signing certificate
- Enterprise telemetry with explicit privacy controls
- Advanced multilingual and scam-family classification

## 11. Expected Outcome
The project provides a demonstrable Windows security application integrating ML classification, explainable threat indicators, user safety guidance, local auditability, testing and a deployable Windows build workflow. It is suitable as an academic/college security project and as a foundation for further production validation.
