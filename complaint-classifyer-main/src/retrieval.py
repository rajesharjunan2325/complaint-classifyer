"""Small local retrieval index built from historical Verizon responses."""
import csv
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def _terms(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))

def load_history(path=None):
    path = path or ROOT / "data" / "raw" / "verizon_historical_responses.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def retrieve(text, intent, history=None, limit=3):
    history = history or load_history()
    query = _terms(text)
    candidates = [row for row in history if row["intent"] == intent] or history
    scored = []
    for row in candidates:
        overlap = len(query & _terms(row["customer_message"]))
        score = overlap + (2 if row["intent"] == intent else 0)
        scored.append((score, row))
    return [row for _, row in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]
