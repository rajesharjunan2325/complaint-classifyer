"""Run the offline evaluation suite and write evaluation/results.json."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation.baseline import trivial, keyword
from evaluation.human_judge_agreement import HUMAN_SUBSET, JUDGE_SUBSET, cohens_kappa
from evaluation.llm_judge import score_reply
from src.intent_classifier import classify, evaluate_model, train_model
from src.pipeline import run
from src.retrieval import retrieve

ROOT = Path(__file__).resolve().parents[1]


def accuracy(actual, predicted):
    return round(sum(a == p for a, p in zip(actual, predicted)) / len(actual), 3) if actual else 0.0


def macro_f1(actual, predicted):
    labels = sorted(set(actual))
    values = []
    for label in labels:
        tp = sum(a == label and p == label for a, p in zip(actual, predicted))
        fp = sum(a != label and p == label for a, p in zip(actual, predicted))
        fn = sum(a == label and p != label for a, p in zip(actual, predicted))
        precision = tp / (tp + fp) if tp + fp else 0
        recall = tp / (tp + fn) if tp + fn else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
        values.append(f1)
    return round(sum(values) / len(values), 3) if values else 0.0


def recall_at_k(items, relevant, k=3):
    top_k = items[:k]
    return 1.0 if relevant in top_k else 0.0


def main():
    golden_path = ROOT / "data" / "golden_set.csv"
    if not golden_path.exists():
        raise SystemExit("golden_set.csv missing; run: python data/generate_golden_set.py")

    with golden_path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    model_bundle = train_model()
    actual = [row["gold_intent"] for row in rows]
    predictions = [classify(row["customer_text"], model_bundle)["intent"] for row in rows]
    majority_predictions = trivial(rows)
    # baseline keyword model kept as a simple and comparable reference
    baseline_predictions = keyword(rows)

    retrieval_scores = []
    reply_scores = []
    escalation_scores = []
    failure_categories = {}

    for row in rows:
        result = run(row["customer_text"])
        predicted_intent = result["classification"]["intent"]
        retrieved = result["retrieval"]
        judged = score_reply(result["response"]["reply"], predicted_intent)
        reply_scores.append(judged["score"])
        retrieval_scores.append(recall_at_k([item["intent"] for item in retrieved], row["gold_intent"], k=3))
        expected_action = row["gold_escalation_decision"]
        actual_action = result["decision"]["action"]
        escalation_scores.append((actual_action == expected_action, expected_action, actual_action))

        if row["gold_intent"] != predicted_intent:
            category = "overlapping language" if result["classification"]["confidence"] >= 0.62 else "ambiguous or underspecified"
            failure_categories.setdefault(category, []).append({
                "customer_text": row["customer_text"],
                "expected": row["gold_intent"],
                "predicted": predicted_intent,
            })

    classifier_metrics = {
        "accuracy": accuracy(actual, predictions),
        "macro_f1": macro_f1(actual, predictions),
        "baseline_majority_accuracy": accuracy(actual, majority_predictions),
        "baseline_keyword_accuracy": accuracy(actual, baseline_predictions),
    }

    per_class = evaluate_model(model_bundle, [(row["customer_text"], row["gold_intent"]) for row in rows])["per_class"]
    classifier_metrics["per_class_f1"] = per_class

    results = {
        "dataset": {
            "name": "Verizon Twitter support golden set",
            "examples": len(rows),
            "intents": sorted(set(actual)),
        },
        "classifier": classifier_metrics,
        "retrieval": {
            "mean_recall_at_3": round(sum(retrieval_scores) / len(retrieval_scores), 3),
            "recall_at_3_examples": retrieval_scores[:10],
        },
        "reply_quality": {
            "mean_rubric_score": round(sum(reply_scores) / len(reply_scores), 3),
            "rubric": ["relevant", "safe", "actionable", "empathetic"],
        },
        "escalation": {
            "accuracy": round(sum(match for match, _, _ in escalation_scores) / len(escalation_scores), 3),
            "auto_handle": sum(action == "auto_handle" for _, _, action in escalation_scores),
            "escalate": sum(action == "escalate" for _, _, action in escalation_scores),
        },
        "human_vs_judge": {
            "subset": len(HUMAN_SUBSET),
            "percentage_agreement": round(sum(a == b for a, b in zip(HUMAN_SUBSET, JUDGE_SUBSET)) / len(HUMAN_SUBSET), 3),
            "cohens_kappa": cohens_kappa(HUMAN_SUBSET, JUDGE_SUBSET),
        },
        "failure_analysis": {
            "categories": failure_categories,
            "required_categories": ["overlapping language", "ambiguous or underspecified", "high-risk language", "missing historical evidence", "unsafe personal-data request"],
        },
    }

    out = ROOT / "evaluation" / "results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
