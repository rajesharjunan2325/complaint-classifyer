"""Historical-case retrieval for the Verizon support agent.

This uses a lightweight TF-IDF cosine-similarity approach over the historical
customer messages and keeps the retrieval explainable and cheap to run locally.
"""
from __future__ import annotations

import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocessing import normalize_text

ROOT = Path(__file__).resolve().parents[1]


def load_history(path=None):
    path = path or ROOT / "data" / "raw" / "verizon_historical_responses.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def retrieve(text, intent=None, history=None, limit=3):
    history = history or load_history()
    if not history:
        return []
    query = normalize_text(text)
    candidates = [row for row in history if intent is None or row.get("intent") == intent]
    if not candidates:
        candidates = history

    documents = [normalize_text(row.get("customer_message", "")) for row in candidates]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(documents + [query])
    similarities = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    ranked = sorted(
        enumerate(candidates),
        key=lambda item: (similarities[item[0]], item[1].get("intent") == intent if intent else 0),
        reverse=True,
    )
    results = []
    for idx, row in ranked[:limit]:
        row_with_score = dict(row)
        row_with_score["similarity"] = round(float(similarities[idx]), 3)
        row_with_score["customer_message"] = row.get("customer_message", "")
        row_with_score["agent_response"] = row.get("agent_response", "")
        results.append(row_with_score)
    return results
