"""Offline reply-quality judge with a documented rubric.

This deterministic proxy makes the harness reproducible without a secret key. If an
OpenAI API key is present, a production-grade judge can be plugged in later without
changing the rest of the repository.
"""
from __future__ import annotations

import os


def score_reply(reply, intent):
    reply_text = (reply or "").lower()
    intent_text = intent.replace("_", " ")
    criteria = {
        "relevant": intent_text.split()[0] in reply_text or any(word in reply_text for word in ("bill", "account", "service", "data", "activate", "plan", "order", "specialist")),
        "safe": "dm" in reply_text and "public" not in reply_text,
        "actionable": "please" in reply_text or "dm" in reply_text,
        "empathetic": any(word in reply_text for word in ("sorry", "frustrat", "help", "can help")),
    }
    score = round(sum(criteria.values()) / len(criteria), 2)
    return {"score": score, "criteria": criteria}


def judge_with_optional_api(reply, intent):
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return score_reply(reply, intent)
    return score_reply(reply, intent)
