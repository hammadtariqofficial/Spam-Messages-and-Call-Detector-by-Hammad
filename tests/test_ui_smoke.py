from __future__ import annotations
import tkinter as tk
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from spam_detector_desktop import App

app = App()
app.update_idletasks()
assert app.winfo_width() >= 980
assert app.winfo_height() >= 660
app.text.insert("1.0", "helo")
app.analyze()
app.update()
assert app.result_badge.cget("text").startswith("NORMAL")
risk_text = app.risk.cget("text")
assert risk_text.endswith("%")
assert 0 <= int(risk_text.rstrip("%")) <= 24
app.clear()
app.text.insert("1.0", "URGENT click this link to verify your bank account and enter OTP")
app.analyze()
app.update()
assert app.result_badge.cget("text").startswith("SPAM")
app._close_app()
print("UI_SMOKE_TEST_PASSED")
