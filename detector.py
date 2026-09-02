from __future__ import annotations
import re, hashlib, json, csv, sqlite3
from pathlib import Path
from datetime import datetime
from typing import Any

import joblib

# PyInstaller --onefile extracts bundled read-only resources to _MEIPASS.
# Keep the SQLite audit database beside the executable (writable), while
# loading bundled ML artifacts from the PyInstaller resource directory.
import sys
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
MODEL_DIR = RESOURCE_DIR / "models"
DATA_DIR = RESOURCE_DIR / "data"
MODEL_PATH = MODEL_DIR / "spam_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"
def _writable_data_dir() -> Path:
    # Never write beside the EXE: Program Files, network folders and read-only
    # locations can block writes. Prefer the per-user LocalAppData directory.
    candidates = []
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        candidates.append(Path(local_appdata) / "SpamMessageCallDetector")
    candidates.append(APP_DIR / "data_store")
    candidates.append(Path.home() / ".spam_message_call_detector")
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".write_test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return candidate
        except Exception:
            continue
    return APP_DIR


import os
USER_DATA_DIR = _writable_data_dir()
DB_PATH = USER_DATA_DIR / "detector_history.db"

URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.I)
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)

RULES = [
    (r"\burgent\b|\bimmediately\b|\bact now\b|\bfinal notice\b", "Urgency or pressure language detected.", 16),
    (r"\bverify\b|\bverification\b|\bconfirm(?:ation)?\b", "Identity/account verification request detected.", 14),
    (r"\baccount\b|\blogin\b|\bsign.?in\b|\bsuspended\b|\blocked\b", "Account or security language detected.", 10),
    (r"\bbank\b|\bcard\b|\bpayment\b|\btransfer\b|\bfee\b|\bcrypto\b", "Financial/payment language detected.", 18),
    (r"\bpassword\b|\bpasscode\b|\bcredential\b|\botp\b|\bone[- ]time password\b", "Sensitive credential/OTP request detected.", 20),
    (r"\bclick\b|\bopen\b|\bvisit\b|\blink\b", "Action to open/click a link detected.", 12),
    (r"\bfree\b|\bbonus\b|\breward\b|\bvoucher\b|\bgift\b|\bcash\b", "Reward/free-offer language detected.", 15),
    (r"\bwinner\b|\bwon\b|\bprize\b|\blottery\b|\bjackpot\b", "Prize/winner language detected.", 28),
    (r"\bcongratulations\b|\bclaim\b|\bselected\b", "Prize/claim wording detected.", 18),
    (r"\bclaim now\b|\breceive now\b|\bcall now\b", "Immediate reward/action language detected.", 12),
    (r"\boffer\b|\bdiscount\b|\bdeal\b|\bpromo\b", "Promotional language detected.", 7),
    (r"\bloan\b|\binvest\b|\bprofit\b|\bdouble your money\b", "Financial solicitation/investment language detected.", 12),
    (r"\bcall\b|\bcall me\b|\bpress\b|\bdial\b|\bhotline\b", "Call-related instruction detected.", 5),
    (r"\bdelivery\b|\btracking\b|\bpackage\b|\bshipment\b", "Delivery/tracking request detected; verify through the official carrier channel.", 8),
    (r"\bpolice\b|\blegal action\b|\barrest\b|\bcourt\b", "Threatening/legal-pressure language detected.", 14),
]

class SpamDetector:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_loaded = False
        self.load_error = ""
        try:
            self.model = joblib.load(MODEL_PATH)
            self.vectorizer = joblib.load(VECTORIZER_PATH)
            self.model_loaded = True
        except Exception as e:
            self.load_error = str(e)

    def _rules(self, text: str):
        score=0.0; reasons=[]
        low=text.lower()
        for pattern, reason, points in RULES:
            if re.search(pattern, low):
                score += points
                reasons.append(reason)
        if URL_RE.search(text):
            score += 16
            reasons.append("Web link present; verify the destination independently.")
        if PHONE_RE.search(text):
            score += 3
            reasons.append("Phone number detected.")
        if EMAIL_RE.search(text):
            score += 2
            reasons.append("Email address detected.")
        if text.count("!") >= 3:
            score += 5
            reasons.append("Attention-grabbing punctuation detected.")
        # Only flag meaningful repeated words. Common words such as
        # "your", "the", "to", etc. must not create a false positive.
        stopwords = {
            "a","an","and","are","as","at","be","by","for","from","has","have",
            "i","if","in","is","it","me","my","of","on","or","our","that","the",
            "this","to","was","we","were","will","with","you","your"
        }
        tokens = re.findall(r"[a-z0-9']+", low)
        meaningful = [t for t in tokens if len(t) > 3 and t not in stopwords]
        repeated = {t for t in meaningful if meaningful.count(t) >= 3}
        if repeated:
            score += 4
            reasons.append("Repeated wording/patterns detected: " + ", ".join(sorted(repeated)[:3]) + ".")

        # Benign-context hard negatives. These patterns are common in real
        # conversations and should not be treated like unsolicited scams.
        benign_contexts = [
            (r"\bsecurity lecture\b.*\bpassword hygiene\b", 18, "Benign security-education context detected."),
            (r"\bteacher\b.*\bpassword\b", 16, "Educational password-management context detected."),
            (r"\bcongratulations on (?:finishing|completing)\b.*\bassignment\b", 18, "Benign congratulations/academic context detected."),
            (r"\bclaim your certificate\b.*\b(office|college)\b", 18, "Certificate collection context detected."),
            (r"\bprize ceremony\b", 24, "Benign ceremony context detected."),
        ]
        for pattern, reduction, note in benign_contexts:
            if re.search(pattern, low):
                score=max(0.0,score-reduction)
                reasons.append(note)
        return min(score,100.0), reasons

    def analyze(self, text: str, sender: str="") -> dict[str,Any]:
        text=" ".join(text.split())
        sender=" ".join(sender.split())
        if not text:
            raise ValueError("Enter a message or call-related text.")
        rule_score,reasons=self._rules(text)
        ml=0.0
        if self.model_loaded:
            try:
                # New industrial model is a full sklearn Pipeline (word +
                # character TF-IDF -> Logistic Regression). Older releases
                # stored a separate vectorizer/model pair, so both formats are
                # supported for backward compatibility.
                if hasattr(self.model, "named_steps") and "features" in self.model.named_steps:
                    p=self.model.predict_proba([text])[0]
                    probs=dict(zip(self.model.classes_,p))
                else:
                    x=self.vectorizer.transform([text])
                    p=self.model.predict_proba(x)[0]
                    probs=dict(zip(self.model.classes_,p))
                ml=float(probs.get(1,p[-1]))
            except Exception as e:
                self.load_error=str(e)
        # Unknown sender is a risk indicator only when sender metadata is supplied.
        unknown_sender = bool(sender and any(x in sender.lower() for x in ("unknown","private","hidden","no caller id")))
        if unknown_sender:
            rule_score=min(100,rule_score+12)
            reasons.append("Sender is marked unknown/private.")
        # Combine independent ML and explainable rule evidence.
        # Certain combinations are strong enough to override ML uncertainty.
        low = text.lower()
        hard_scam = (
            (re.search(r"\b(bank|card|payment|account)\b", low)
             and re.search(r"\b(otp|password|passcode|credential)\b", low)
             and re.search(r"\b(click|link|verify|confirm)\b", low))
            or
            (re.search(r"\b(won|winner|prize|lottery|jackpot)\b", low)
             and re.search(r"\b(free|cash|reward|gift|voucher)\b", low)
             and re.search(r"\b(claim|call|click|receive)\b", low))
            or
            (re.search(r"\b(free|bonus|reward|gift|voucher)\b", low)
             and re.search(r"\b(click|claim|collect|receive)\b", low))
            or
            (re.search(r"\b(payment|card)\b", low)
             and re.search(r"\b(update|failed|pending)\b", low)
             and re.search(r"\b(link|details|verify)\b", low))
            or
            (re.search(r"\b(investment|invest|loan)\b", low)
             and re.search(r"\b(fee|profit|release)\b", low)
             and re.search(r"\b(pay|send|transfer|guaranteed)\b", low))
        )
        combined = (ml * 100.0 * 0.65) + (rule_score * 0.35) if ml else rule_score
        risk = min(100.0, max(rule_score, combined))
        if hard_scam:
            risk = max(risk, 85.0)
        moderate_request = (
            re.search(r"\b(verify|confirm|check)\b", low)
            and re.search(r"\b(account|invoice|payment|booking|registration|delivery|tracking)\b", low)
            and not re.search(r"\b(urgent|immediately|click|http|www|otp|password|passcode|credential|claim now|call now|final notice|suspended|attached link|now)\b", low)
        )
        if moderate_request and not hard_scam:
            risk = min(risk, 65.0)

        benign_context = (
            re.search(r"\b(security lecture|password hygiene|teacher.*password)\b", low)
            or re.search(r"\b(congratulations on .*assignment|college competition|claim your certificate.*(office|college)|prize ceremony)\b", low)
            or re.search(r"\b(confirm the delivery time|office order|official app)\b", low)
        )
        if benign_context and not hard_scam and not unknown_sender:
            risk = min(risk, 24.0)
        if unknown_sender and not hard_scam:
            risk = max(risk, 25.0)
        if risk >= 70:
            classification="SPAM"
            level="CRITICAL"
            rec="Do not click links, call unknown numbers, send money, or share passwords/OTPs. Verify through an official channel."
        elif risk >= 25:
            classification="SUSPICIOUS"
            level="WARNING"
            rec="Do not act immediately. Verify the sender, destination and request independently before responding."
        else:
            classification="NORMAL"
            level="LOW"
            rec="No strong spam indicators were detected. Continue using normal security precautions."
        if not reasons:
            reasons=["No strong suspicious patterns were detected."]
        return {
            "classification":classification,
            "severity":level,
            "risk_score":round(risk,2),
            "ml_probability":round(ml*100,2),
            "rule_score":round(rule_score,2),
            "reasons":reasons[:10],
            "recommendation":rec,
            "sender":sender,
            "text":text,
            "timestamp":datetime.now().isoformat(timespec="seconds")
        }

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS scans(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, sender TEXT, classification TEXT,
            severity TEXT, risk REAL, ml_probability REAL,
            text_hash TEXT, text TEXT, reasons TEXT
        )""")
        con.commit()

def save_scan(result):
    init_db()
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""INSERT INTO scans
        (timestamp,sender,classification,severity,risk,ml_probability,text_hash,text,reasons)
        VALUES(?,?,?,?,?,?,?,?,?)""", (
            result["timestamp"],result["sender"],result["classification"],
            result["severity"],result["risk_score"],result["ml_probability"],
            hashlib.sha256(result["text"].encode()).hexdigest(),
            result["text"],json.dumps(result["reasons"])
        ))
        con.commit()

def history(limit=100):
    init_db()
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory=sqlite3.Row
        rows=con.execute("SELECT * FROM scans ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
        return [dict(r) for r in rows]
