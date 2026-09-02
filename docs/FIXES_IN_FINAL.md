# Final QA / Fix Log

## Bugs corrected
1. PyInstaller one-file resource lookup: ML files now load from `_MEIPASS`.
2. Audit database remains writable beside the EXE.
3. Generic repeated-word detection caused false positives; it is now stopword-aware and only triggers on meaningful repetition.
4. Rule score is presented as an indicator score (`/100`) rather than pretending it is an ML probability.
5. Strong scam combinations (bank/account + credential + action; or prize + reward + claim/call/click) receive a high-confidence risk floor.
6. ML loading is explicitly verified before the final test.
7. Windows EXE build script includes explicit sklearn/joblib imports and collected sklearn data for better PyInstaller reliability.
8. A final verification script was added for model loading and representative Normal/Spam tests.

## Requirement coverage
Normal → Suspicious → Spam classification, suspicious links, urgency, promotional content, sensitive information requests, unknown sender context, explanation, risk score, safety recommendations, dashboard, history, export, testing documentation, and one-file EXE build are included.

## Limitation
A native Windows binary cannot be compiled in this Linux execution environment. `BUILD_ONE_EXE.bat` builds the actual Windows one-file executable on Windows.
