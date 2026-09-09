"""Two explicit classifier baselines required by the assignment."""
from __future__ import annotations

from collections import Counter


def _get_label(row):
    return row.get("gold_intent") or row.get("intent") or row.get("label")


def _get_text(row):
    return row.get("customer_text") or row.get("text") or row.get("customer_message") or ""


def trivial(rows):
    labels = [_get_label(row) for row in rows]
    majority = Counter(labels).most_common(1)[0][0]
    return [majority] * len(rows)


def keyword(rows):
    from src.intent_classifier import classify

    return [classify(_get_text(row))["intent"] for row in rows]
