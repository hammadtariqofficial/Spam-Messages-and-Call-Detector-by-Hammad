from detector import SpamDetector

d = SpamDetector()
assert d.model_loaded, f"ML model failed to load: {d.load_error}"

cases = [
    ("Hey bro, are you coming to college tomorrow?", "NORMAL"),
    ("URGENT! Your bank account has been suspended. Click this link immediately to verify your account and enter your OTP.", "SPAM"),
    ("Congratulations! You won a free cash prize. Claim now to receive your reward. Call now!", "SPAM"),
]
for text, expected in cases:
    r = d.analyze(text)
    print(f"{expected:8} -> {r['classification']:8} | risk={r['risk_score']:.0f}% | ml={r['ml_probability']:.2f}%")
    assert r["classification"] == expected, (expected, r)

print("FINAL VERIFICATION PASSED")
