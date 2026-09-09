"""Auto-handle versus escalation policy for the support agent."""
from __future__ import annotations

RISK_TERMS = {"fraud", "stolen", "scam", "lawsuit", "legal", "safety", "threat", "death", "harassment"}


def decide(classification, text, retrieval=None):
    lowered = text.lower()
    reasons = []
    confidence = float(classification.get("confidence", 0.0))
    retrieval_score = 0.0
    if retrieval:
        retrieval_score = float(sum(item.get("similarity", 0.0) for item in retrieval) / len(retrieval))

    if confidence < 0.68:
        reasons.append("intent confidence is below the calibrated auto-handle threshold")
    if retrieval_score < 0.18 and retrieval is not None:
        reasons.append("retrieval does not have enough supporting historical similarity")
    if classification.get("urgent") or any(term in lowered for term in RISK_TERMS):
        reasons.append("high-risk or urgent language requires human review")
    if classification.get("intent") == "human_support":
        reasons.append("the user explicitly asks for a specialist or secure handoff")

    action = "escalate" if reasons else "auto-handle"
    reason_text = reasons or ["confidence, retrieval, and risk checks all passed"]
    return {
        "action": action,
        "reasons": reason_text,
        "confidence_threshold": 0.68,
        "retrieval_similarity_threshold": 0.18,
        "retrieval_similarity": round(retrieval_score, 3),
    }
