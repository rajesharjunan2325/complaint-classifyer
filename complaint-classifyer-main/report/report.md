# Twitter Customer Support AI Agent

## Scope

Brand: **Verizon**. Channel: public Twitter/X customer support. The system classifies eight intents, retrieves similar historical responses, drafts a safe reply, and chooses auto-handle or escalation.

## Evaluation contract

The golden set contains 200 labeled examples: 25 per intent. Run `python data/generate_golden_set.py` to reproduce it, then `python evaluation/run_evaluation.py` to write `evaluation/results.json`.

Metrics include accuracy, macro-F1, trivial-majority and keyword baselines, reply rubric score, auto-handle/escalation counts, and Cohen's kappa on a 20-example human-vs-judge subset.

## Known failure categories

1. Overlapping language: "my phone is slow" may mean device or data.
2. Ambiguous or underspecified: "help, nothing works" lacks a routeable intent.
3. High-risk language: fraud, legal, safety, and threats require human review.
4. Missing historical evidence: novel requests fall back to the closest example.
5. Unsafe personal-data request: replies must move identity checks into a secure DM.

The current offline judge is a deterministic rubric proxy, intentionally labeled as such. It is not presented as a claim about a hosted LLM's quality.
