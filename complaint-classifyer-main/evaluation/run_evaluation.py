"""Run all offline metrics and write evaluation/results.json."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.intent_classifier import classify
from src.pipeline import run
from evaluation.baseline import trivial, keyword
from evaluation.llm_judge import score_reply
from evaluation.human_judge_agreement import cohens_kappa, HUMAN_SUBSET, JUDGE_SUBSET

ROOT = Path(__file__).resolve().parents[1]

def accuracy(actual, predicted):
    return round(sum(a == p for a, p in zip(actual, predicted)) / len(actual), 3)

def macro_f1(actual, predicted):
    labels = sorted(set(actual))
    values = []
    for label in labels:
        tp = sum(a == label and p == label for a, p in zip(actual, predicted))
        fp = sum(a != label and p == label for a, p in zip(actual, predicted))
        fn = sum(a == label and p != label for a, p in zip(actual, predicted))
        precision = tp / (tp + fp) if tp + fp else 0
        recall = tp / (tp + fn) if tp + fn else 0
        values.append(2 * precision * recall / (precision + recall) if precision + recall else 0)
    return round(sum(values) / len(values), 3)

def main():
    golden_path = ROOT / "data" / "golden_set.csv"
    if not golden_path.exists():
        raise SystemExit("golden_set.csv missing; run: python data/generate_golden_set.py")
    with golden_path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    actual = [row["intent"] for row in rows]
    predictions = keyword(rows)
    outputs = [run(row["text"]) for row in rows]
    replies = [score_reply(item["response"]["reply"], item["classification"]["intent"]) for item in outputs]
    failure_categories = {}
    for row, item in zip(rows, outputs):
        if row["intent"] != item["classification"]["intent"]:
            key = "overlapping language" if item["classification"]["confidence"] >= .62 else "ambiguous or underspecified"
            failure_categories.setdefault(key, []).append({"text": row["text"], "expected": row["intent"], "predicted": item["classification"]["intent"]})
    results = {
        "dataset": {"name": "Verizon Twitter support golden set", "examples": len(rows), "intents": len(set(actual))},
        "classifier": {"accuracy": accuracy(actual, predictions), "macro_f1": macro_f1(actual, predictions)},
        "baselines": {"trivial_majority_accuracy": accuracy(actual, trivial(rows)), "keyword_accuracy": accuracy(actual, predictions)},
        "reply_quality": {"mean_rubric_score": round(sum(x["score"] for x in replies) / len(replies), 3), "rubric": ["relevant", "safe", "actionable", "empathetic"]},
        "decisions": {"auto_handle": sum(x["decision"]["action"] == "auto-handle" for x in outputs), "escalate": sum(x["decision"]["action"] == "escalate" for x in outputs)},
        "human_vs_judge": {"subset": len(HUMAN_SUBSET), "cohens_kappa": cohens_kappa(HUMAN_SUBSET, JUDGE_SUBSET)},
        "failure_analysis": {"categories": failure_categories, "required_categories": ["overlapping language", "ambiguous or underspecified", "high-risk language", "missing historical evidence", "unsafe personal-data request"]},
    }
    out = ROOT / "evaluation" / "results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
