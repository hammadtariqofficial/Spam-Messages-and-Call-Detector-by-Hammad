from detector import SpamDetector
d=SpamDetector()
cases=[
 ("Please send me the project report tomorrow.","NORMAL"),
 ("URGENT click this link to verify your bank account immediately","SPAM"),
 ("Congratulations you won a free cash prize claim now","SPAM"),
 ("Your delivery needs confirmation, please check the tracking portal","SUSPICIOUS"),
]
for text,expected in cases:
    r=d.analyze(text)
    print(f"{expected:10} -> {r['classification']:10} {r['risk_score']:>6}% | {text}")
    assert r["classification"] == expected, (text, r)
print("All smoke tests passed.")
