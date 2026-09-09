"""Deterministic, explainable intent classifier for the Verizon support slice."""
import re

INTENTS = {
    "billing_payment": {"label": "Billing & payment", "keywords": ["bill", "billing", "charge", "charged", "payment", "refund", "credit", "fee"]},
    "account_access": {"label": "Account access", "keywords": ["login", "log in", "password", "locked", "account", "verify", "sign in"]},
    "network_outage": {"label": "Network outage", "keywords": ["outage", "down", "no service", "signal", "network", "emergency calls", "coverage"]},
    "slow_data": {"label": "Slow data", "keywords": ["slow", "5g", "4g", "data", "internet", "buffering", "speed"]},
    "device_activation": {"label": "Device activation", "keywords": ["activate", "activation", "esim", "sim", "device", "phone", "upgrade"]},
    "plan_change": {"label": "Plan change", "keywords": ["plan", "upgrade", "downgrade", "add a line", "cancel", "unlimited"]},
    "delivery_status": {"label": "Order & delivery", "keywords": ["order", "shipping", "delivery", "tracking", "arrive", "package", "shipment"]},
    "human_support": {"label": "Human support", "keywords": ["agent", "human", "representative", "dm", "help", "contact", "complaint"]},
}

URGENT = {"urgent", "asap", "emergency", "fraud", "stolen", "scam", "lawsuit", "legal", "safety"}

def _tokens(text):
    return set(re.findall(r"[a-z0-9']+", text.lower()))

def classify(text):
    tokens = _tokens(text)
    scores = {}
    for intent, spec in INTENTS.items():
        score = 0
        for keyword in spec["keywords"]:
            key_tokens = set(keyword.split())
            score += (2 if key_tokens <= tokens else 0) + (1 if keyword in text.lower() else 0)
        scores[intent] = score
    best = max(scores, key=scores.get)
    ranked = sorted(scores.values(), reverse=True)
    raw = scores[best]
    margin = raw - (ranked[1] if len(ranked) > 1 else 0)
    confidence = min(0.98, 0.42 + raw * 0.08 + margin * 0.06) if raw else 0.18
    return {"intent": best if raw else "human_support", "label": INTENTS[best if raw else "human_support"]["label"], "confidence": round(confidence, 2), "scores": scores, "urgent": bool(tokens & URGENT)}
