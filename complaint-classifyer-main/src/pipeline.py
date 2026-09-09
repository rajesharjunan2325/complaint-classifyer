"""End-to-end Verizon support agent pipeline."""
from __future__ import annotations

from .escalation import decide
from .intent_classifier import classify
from .reply_generator import generate_reply
from .retrieval import retrieve


def run(text: str):
    classification = classify(text)
    history = retrieve(text, classification["intent"], limit=3)
    response = generate_reply(classification["intent"], history, text)
    decision = decide(classification, text, history)
    return {
        "text": text,
        "classification": classification,
        "retrieval": history,
        "response": response,
        "decision": decision,
    }


__all__ = ["run"]
