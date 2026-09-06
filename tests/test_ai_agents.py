from __future__ import annotations
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai_agents import AIAgentOrchestrator

# Offline behavior must be deterministic and must never require a live API key.
os.environ.pop("GEMINI_API_KEY", None)
a = AIAgentOrchestrator()
r = a.run("hello", "", {"classification":"NORMAL", "risk_score":10, "ml_probability":50, "rule_score":0, "reasons":[]})
assert r["enabled"] is False
assert r["status"] == "OFFLINE / OPTIONAL"
print("AI_AGENT_OFFLINE_TEST_PASSED")
