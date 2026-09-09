"""Lightweight preprocessing utilities used before intent classification and retrieval."""
from __future__ import annotations

import re


def normalize_text(text: str | None) -> str:
    if text is None:
        return ""
    value = str(text).lower()
    value = re.sub(r"https?://\S+|www\.\S+", " ", value)
    value = re.sub(r"@[A-Za-z0-9_]+", " ", value)
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def tokenize(text: str | None) -> list[str]:
    cleaned = normalize_text(text)
    return cleaned.split() if cleaned else []


__all__ = ["normalize_text", "tokenize"]