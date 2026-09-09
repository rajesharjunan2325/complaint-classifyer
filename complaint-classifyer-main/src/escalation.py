"""Risk and confidence policy for deciding auto-handle vs human review."""

def decide(classification, text):
    lowered = text.lower()
    risk_terms = {"fraud", "stolen", "scam", "lawsuit", "legal", "safety", "threat", "death"}
    reasons = []
    if classification["confidence"] < 0.62:
        reasons.append("low classifier confidence")
    if classification["urgent"] or any(term in lowered for term in risk_terms):
        reasons.append("urgent or high-risk language")
    if classification["intent"] == "human_support":
        reasons.append("request is better handled by a specialist")
    action = "escalate" if reasons else "auto-handle"
    return {"action": action, "reasons": reasons or ["confidence and risk checks passed"]}
