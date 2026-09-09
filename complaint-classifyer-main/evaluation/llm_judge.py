"""Offline reply-quality judge with a documented rubric.
This deterministic proxy makes the harness reproducible; replace score_reply with an
API-backed judge only when credentials and a pinned model are available.
"""
def score_reply(reply, intent):
    criteria = {
        "relevant": intent.replace("_", " ").split()[0] in reply.lower() or any(word in reply.lower() for word in ("bill", "account", "service", "data", "activate", "plan", "order", "specialist")),
        "safe": "dm" in reply.lower() and "public" in reply.lower(),
        "actionable": "please" in reply.lower(),
        "empathetic": any(word in reply.lower() for word in ("sorry", "frustrat", "help")),
    }
    return {"score": round(sum(criteria.values()) / len(criteria), 2), "criteria": criteria}
