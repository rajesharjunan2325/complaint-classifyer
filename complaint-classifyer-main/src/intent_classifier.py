"""Trainable intent classifier for the Verizon support slice.

This version keeps the pipeline simple, deterministic, and fully reproducible on a
normal laptop. It also exposes training/evaluation utilities needed for the Hiver
assignment without depending on a hosted model.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from .preprocessing import normalize_text

ROOT = Path(__file__).resolve().parents[1]

INTENTS = {
    "account_access": "Account access",
    "billing_issue": "Billing issue",
    "device_activation": "Device activation",
    "delivery_issue": "Delivery issue",
    "network_outage": "Network outage",
    "plan_change": "Plan change",
    "slow_data": "Slow data",
    "human_support": "Human support",
}

TRAINING_EXAMPLES = {
    "account_access": [
        "cannot log in to my verizon account",
        "password reset not working",
        "my account is locked after entering wrong password",
        "sign in keeps failing on my app",
        "i forgot my account password",
        "verification code never arrives",
        "my app says account not recognized",
        "login loop on verizon app",
        "help me get back into my account",
        "my profile is locked",
    ],
    "billing_issue": [
        "why is my bill higher than usual",
        "charge on my account looks wrong",
        "i was double charged this month",
        "refund request after billing error",
        "my bill is unexpectedly high",
        "payment failed but i was charged",
        "credit not applied to account",
        "why was there a late fee",
        "billing dispute for my phone bill",
        "there is a duplicate charge on my account",
    ],
    "device_activation": [
        "new phone will not activate",
        "my sim activation failed",
        "i cannot activate this device",
        "esim setup is not complete",
        "phone says not activated",
        "activation stuck on my new phone",
        "help activate my line on a new phone",
        "cannot complete device setup",
        "activation issue after replacing sim",
        "my device is not working after switch",
    ],
    "delivery_issue": [
        "where is my order",
        "my shipment has not arrived",
        "when will my phone be delivered",
        "tracking says package is delayed",
        "order is missing and not shipped",
        "i need a delivery update",
        "package lost in transit",
        "when will my order arrive",
        "my device is stuck in shipping",
        "tracking number is not updating",
    ],
    "network_outage": [
        "verizon service is down in my area",
        "no signal and cannot call",
        "outage in my neighborhood",
        "network is not working today",
        "my calls are failing",
        "sudden loss of service",
        "coverage is down near me",
        "emergency calls failing in my area",
        "service outage affecting my home",
        "internet and signal are completely down",
    ],
    "plan_change": [
        "i want to switch plans",
        "can i downgrade my plan",
        "help me add a line to my account",
        "upgrade to unlimited plan",
        "cancel my plan this month",
        "i need to change my mobile plan",
        "compare my current plan options",
        "remove add on from my account",
        "change to a better plan",
        "my plan needs more data",
    ],
    "slow_data": [
        "5g is painfully slow",
        "internet data is buffering all day",
        "my connection is extremely slow",
        "phone has poor mobile data speed",
        "slow upload and download speeds",
        "data is unusable at home",
        "coverage is weak and speeds are low",
        "network is lagging in my area",
        "my hotspot is crawling",
        "lte service feels very slow",
    ],
    "human_support": [
        "i need a real person to help",
        "please connect me with an agent",
        "this needs human support",
        "please dm me this issue",
        "i want to speak with a specialist",
        "requesting support representative",
        "i need help from a human",
        "please contact me privately",
        "this is a complaint and needs review",
        "send me a secure dm for support",
    ],
}

URGENT_TERMS = {
    "urgent", "asap", "fraud", "stolen", "scam", "lawsuit", "legal", "safety", "threat", "arrest"
}


def _make_model() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, strip_accents="unicode")),
        ("clf", LinearSVC(C=1.0, class_weight="balanced")),
    ])


def build_training_data() -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    for intent, texts in TRAINING_EXAMPLES.items():
        for text in texts:
            rows.append((normalize_text(text), intent))
    return rows


def train_model(train_rows: Iterable[Tuple[str, str]] | None = None) -> dict:
    rows = list(train_rows) if train_rows is not None else build_training_data()
    texts, labels = zip(*rows)
    X_train, X_temp, y_train, y_temp = train_test_split(
        list(texts), list(labels), test_size=0.25, random_state=42, stratify=list(labels)
    )
    X_valid, X_test, y_valid, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )
    model = _make_model()
    model.fit(X_train, y_train)
    return {
        "model": model,
        "train": (X_train, y_train),
        "valid": (X_valid, y_valid),
        "test": (X_test, y_test),
        "labels": list(INTENTS.keys()),
    }


def _softmax(logits: np.ndarray) -> np.ndarray:
    logits = logits - np.max(logits)
    exps = np.exp(logits)
    return exps / np.sum(exps)


def classify(text: str, model_bundle: dict | None = None) -> dict:
    bundle = model_bundle or train_model()
    model = bundle["model"]
    cleaned = normalize_text(text)
    if not cleaned:
        cleaned = "customer support"
    prediction = model.predict([cleaned])[0]
    decision = model.decision_function([cleaned])[0]
    probs = _softmax(decision)
    intent_index = list(bundle["labels"]).index(prediction)
    confidence = float(np.clip(probs[intent_index], 0.0, 1.0))
    return {
        "intent": prediction,
        "label": INTENTS[prediction],
        "confidence": round(confidence, 3),
        "scores": {label: float(score) for label, score in zip(bundle["labels"], probs)},
        "urgent": bool(set(cleaned.split()) & URGENT_TERMS),
    }


def evaluate_model(model_bundle: dict | None = None, rows: Iterable[Tuple[str, str]] | None = None) -> dict:
    bundle = model_bundle or train_model()
    texts, labels = zip(*rows) if rows is not None else zip(*build_training_data())
    predictions = bundle["model"].predict(list(texts))
    labels_order = list(INTENTS.keys())
    cm = confusion_matrix(labels, predictions, labels=labels_order)
    report = precision_recall_fscore_support(labels, predictions, labels=labels_order, average=None, zero_division=0)
    precision, recall, f1, _ = report
    metrics = {
        "accuracy": round(float(accuracy_score(labels, predictions)), 3),
        "macro_f1": round(float(f1_score(labels, predictions, labels=labels_order, average="macro", zero_division=0)), 3),
        "per_class": {
            label: {
                "precision": round(float(p), 3),
                "recall": round(float(r), 3),
                "f1": round(float(f), 3),
            }
            for label, p, r, f in zip(labels_order, precision, recall, f1)
        },
        "confusion_matrix": cm.tolist(),
        "labels": labels_order,
    }
    return metrics


def _default_bundle() -> dict:
    return train_model()


__all__ = ["INTENTS", "TRAINING_EXAMPLES", "build_training_data", "train_model", "classify", "evaluate_model"]
