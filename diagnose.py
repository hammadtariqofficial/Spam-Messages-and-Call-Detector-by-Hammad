from detector import SpamDetector
d=SpamDetector()
print("ML ENGINE:", "ONLINE" if d.model_loaded else "FAILED")
if not d.model_loaded:
    print("LOAD ERROR:", d.load_error)
else:
    for text in [
        "Hey bro, are you coming to college tomorrow?",
        "URGENT! Your bank account has been suspended. Click this link immediately to verify your account and enter your OTP."
    ]:
        print(d.analyze(text)["classification"], d.analyze(text)["risk_score"])
