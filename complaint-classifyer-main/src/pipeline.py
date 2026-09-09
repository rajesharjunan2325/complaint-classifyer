"""End-to-end Twitter customer-support agent."""
from .intent_classifier import classify
from .retrieval import retrieve
from .reply_generator import generate_reply
from .escalation import decide

def run(text):
    classification = classify(text)
    history = retrieve(text, classification["intent"])
    response = generate_reply(classification["intent"], history)
    decision = decide(classification, text)
    return {"text": text, "classification": classification, "retrieval": history, "response": response, "decision": decision}
