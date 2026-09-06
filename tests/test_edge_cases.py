from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from detector import SpamDetector

CASES = [
    ("NORMAL", "helo", ""),
    ("NORMAL", "hello", ""),
    ("NORMAL", "hi", ""),
    ("NORMAL", "hey bro", ""),
    ("NORMAL", "good morning", ""),
    ("NORMAL", "good evening", ""),
    ("NORMAL", "how are you", ""),
    ("NORMAL", "thanks", ""),
    ("NORMAL", "thank you", ""),
    ("NORMAL", "ok", ""),
    ("NORMAL", "assalam o alaikum", ""),
    ("NORMAL", "salam", ""),
    ("NORMAL", "kya haal hai", ""),
    ("NORMAL", "kaise ho", ""),
    ("NORMAL", "good luck", ""),
    ("NORMAL", "take care", ""),
    ("SPAM", "hello urgent click this link to verify your bank account and enter OTP", ""),
    ("SUSPICIOUS", "hello please confirm the delivery tracking number", ""),
    ("SUSPICIOUS", "hello", "Unknown"),
    ("NORMAL", "hello, how are you?", ""),
]

d = SpamDetector()
failures = []
for i, (expected, text, sender) in enumerate(CASES, 1):
    result = d.analyze(text, sender)
    if result["classification"] != expected:
        failures.append({"id": i, "expected": expected, "actual": result["classification"], "risk": result["risk_score"], "text": text})

report = {"total_cases": len(CASES), "passed": len(CASES)-len(failures), "failed": len(failures), "failures": failures}
print(json.dumps(report, indent=2))
if failures:
    raise SystemExit(1)
