# Twitter Customer Support AI Agent

A reproducible, evaluation-first adaptation of the original complaint classifier for **Verizon** Twitter support.

## Flow

Customer tweet -> intent + confidence -> historical-response retrieval -> grounded reply -> risk/confidence routing -> auto-handle or human escalation.

## Run the evidence

Requires Python 3.9+; no third-party packages are needed.

```powershell
python data/generate_golden_set.py
python evaluation/run_evaluation.py
```

The evaluator writes `evaluation/results.json`. It reports classifier accuracy and macro-F1, two baselines, reply-quality rubric scores, routing counts, five failure-analysis categories, and human-vs-judge Cohen's kappa.

## Run the UI

Open `index.html` directly in a browser. It is an offline demo of the same decision flow. The browser classifier mirrors the explicit intent definitions in `src/intent_classifier.py` and does not send text to a server.

## Repository map

- `data/raw/verizon_historical_responses.csv`: historical response evidence.
- `data/golden_set.csv`: generated 200-row labeled evaluation set.
- `src/`: classifier, retrieval, reply, escalation, and pipeline modules.
- `evaluation/`: baselines, metrics, reply judge, agreement, and results.
- `report/`: assignment report and 12-item decision log.

## Limitations

This is an offline prototype, not a production moderation or account-support system. The reply judge is a transparent rubric proxy, and the small historical file is illustrative. Production use needs policy review, authenticated tooling, rate limits, audit logging, and a larger independently sampled dataset.
