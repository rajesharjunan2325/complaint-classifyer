"""Two explicit classifier baselines required by the assignment."""
from collections import Counter

def trivial(rows):
    majority = Counter(row["intent"] for row in rows).most_common(1)[0][0]
    return [majority] * len(rows)

def keyword(rows):
    from src.intent_classifier import classify
    return [classify(row["text"])["intent"] for row in rows]
