# Project 7 — Technical Specification & Testing Plan

## Detection flow
Input → normalization → ML probability → explainable rule analysis → weighted risk score → Normal/Suspicious/Spam → safety recommendation → audit history.

## Classification
- 0–29: NORMAL
- 30–69: SUSPICIOUS
- 70–100: SPAM

## Test categories
1. Safe personal messages
2. Banking/payment scams
3. OTP/password requests
4. Prize/reward scams
5. Suspicious URLs
6. Urgent account suspension messages
7. Call-related pressure
8. Unknown/private caller metadata
9. Promotional spam
10. False-positive review

## Security design
No automatic link opening, payment action, call placement, credential collection, or destructive system operation is performed by the application.
