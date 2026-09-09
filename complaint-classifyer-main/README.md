# Complaint Classifyer: Verizon Support Agent

## 1. Project title
Complaint Classifyer: AI Customer Support Agent for Verizon support conversations.

## 2. Problem statement
The assignment asks for an AI customer-support agent that can classify a customer tweet, retrieve similar historical cases, draft a grounded reply, and decide whether to auto-handle or escalate. The system must be explainable, reproducible, and built around historical brand-specific evidence rather than unsupported policy guesses.

## 3. Assignment interpretation
This repository implements the required pipeline:

Customer Tweet -> Preprocessing -> Intent Classification -> Confidence Score -> Historical Case Retrieval -> Grounded Reply Generation -> Auto-handle / Escalate Decision -> Final Response

The project keeps the implementation lightweight and reliable: no unnecessary production stack, no hidden API calls, and no hard-coded secrets. The code stays modular and runs on a normal laptop.

## 4. Dataset
The project uses the Customer Support on Twitter dataset, filtered to a single brand: Verizon.

Selected brand: Verizon
Reason: Verizon is one of the most common single-brand support slices in public social support data and has clear recurring issues such as account access, billing, slow data, delivery, and outage reports. Using a single brand keeps the historical support patterns coherent and makes retrieval grounded in brand-specific evidence.

The historical evidence file is in data/raw/verizon_historical_responses.csv, and the evaluation dataset is in data/golden_set.csv.

## 5. Intent taxonomy
The classifier organizes customer issues into eight support intents:

- account_access
- billing_issue
- device_activation
- delivery_issue
- network_outage
- plan_change
- slow_data
- human_support

These intents were chosen after inspecting the Verizon support language in the historical training slice and preserving the common support categories without over-fragmenting the taxonomy.

## 6. System architecture
- src/preprocessing.py: normalization and tokenization
- src/intent_classifier.py: baseline + improved classifier and confidence estimation
- src/retrieval.py: TF-IDF cosine similarity over historical customer messages
- src/reply_generator.py: grounded reply templates backed by historical support responses
- src/escalation.py: rule-based auto-handle vs escalate policy
- src/pipeline.py: end-to-end agent workflow

## 7. Baselines
The repository includes at least two baselines:

1. Trivial majority baseline
2. Keyword similarity baseline (used as the explicit classifier reference)

The final approach is a simple TF-IDF + Linear SVM classifier because it is fast, explainable, and performs well on short support texts.

## 8. Final approach
The final agent uses:

- normalized tweet text
- TF-IDF vectorizer
- Linear SVC for intent prediction
- confidence score from the margin distribution
- historical retrieval from Verizon support examples
- grounded templates that request secure DM handoff rather than exposing account details publicly
- escalation triggers when confidence or retrieval is weak or language is risky

## 9. Retrieval approach
Historical support retrieval is implemented with TF-IDF cosine similarity over historical customer messages. The system:

- tokenizes and normalizes the new customer tweet
- compares it to historical Verizon customer messages
- chooses the top matching examples for the predicted intent
- returns the customer message and agent response as evidence

This is a lightweight retrieval method and does not require an expensive embedding model.

## 10. Reply generation
The reply generator uses the predicted intent and retrieved evidence to draft a safe reply. It never invents unsupported policies or promises. The agent always asks the customer to move sensitive account details into a secure DM and keeps the response grounded in historical Verizon support language.

## 11. Escalation policy
Escalation is triggered when any of these conditions hold:

- intent confidence is below the calibrated threshold
- historical retrieval similarity is weak
- the user asks for a specialist or secure support handoff
- urgent or risky language is detected

Auto-handle is used only when confidence, retrieval, and safety checks pass.

## 12. Evaluation methodology
The evaluation uses:

- accuracy
- macro F1
- per-class precision/recall/F1
- confusion matrix
- retrieval recall@3
- groundedness/relevance via offline rubric
- escalation accuracy
- human agreement with the LLM-style judge subset

## 13. Results
The evaluation script is designed to produce the metrics in evaluation/results.json by running:

```bash
python data/generate_golden_set.py
python evaluation/run_evaluation.py
```

Results are generated from the golden set and reported in the output JSON. If the environment has not run the evaluation yet, the metric fields are marked as “to be generated” until the script is executed.

## 14. Golden set
The golden set is stored in data/golden_set.csv and contains fields such as:

- tweet_id
- customer_text
- gold_intent
- gold_response_quality
- gold_escalation_decision
- notes

The examples were created as a labeled evaluation set to avoid using the golden set for model training. This keeps the evaluation realistic and reduces leakage from the benchmark into retrieval and training.

## 15. LLM judge
This project includes an offline judge that scores reply quality without requiring an API key. A production OpenAI-based judge can be added later via OPENAI_API_KEY, but the default behavior remains deterministic and local so the repository is runnable offline.

The default rubric checks:

- relevance
- safety
- actionability
- empathy

The judge is intentionally transparent and not presented as a perfect stand-in for a production policy model.

## 16. Human agreement
A small agreement script compares human labels against judge labels and computes percentage agreement and Cohen’s kappa. This is a limited sample and should be interpreted cautiously because human labels are small and subject to individual interpretation.

## 17. Top 5 failure modes
1. Overlapping language between data-speed and device issues
2. Ambiguous or underspecified requests
3. High-risk language requiring human review
4. Missing historical evidence for novel issues
5. Unsafe personal-data requests in a public channel

## 18. What is misleading about my headline number?
### What is misleading about my headline number?
A headline metric like single-number accuracy looks strong, but it can hide meaningful gaps. In a support-agent task, class imbalance, retrieval quality, poor calibration, and limited evaluation samples can make a model look better than it is in production. A small golden set can overstate confidence; a judge can be biased; and if the real-world distribution shifts, the best offline number may still fail in deployment. This is why the right question is not “what is the best score?” but “what does this score actually tell us about robustness, safety, and real support quality?”

## 19. One-week next steps
Prioritized next actions:

1. Improve difficult intent classes
2. Improve retrieval quality for sparse or overlapping cases
3. Calibrate escalation thresholds on validation data
4. Improve response grounding and evidence traceability
5. Expand the evaluation dataset and human-review set

## 20. Decision log
See report/decision_log.md for the engineering decisions, trade-offs, and rationale.

## 21. Installation
```bash
pip install -r requirements.txt
```

## 22. How to run
```bash
python data/generate_golden_set.py
python train.py
python evaluation/run_evaluation.py
python app.py
```

## 23. Example input/output
Example input:

```text
@VerizonSupport My 5G is painfully slow this morning. Please help.
```

Example output:

```text
Intent: slow_data
Confidence: 0.83
Decision: AUTO-HANDLE
Reason: confidence and retrieval checks passed
```

## 24. Limitations
- Golden set is small and synthetic enough to be reproducible, not representative of the full live dataset
- Historical retrieval is intentionally lightweight and may miss long-tail issues
- Offline judge is a rubric proxy, not a full LLM safety judge
- Production deployment would require policy review, authentication, logging, and broader evaluation

## 25. Repository structure
- data/
- data/raw/
- data/processed/
- data/golden_set.csv
- src/
- evaluation/
- report/
- notebooks/
- requirements.txt
- README.md

## 26. Quick note on reproducibility
This repository is designed to be reproducible in under 15 minutes on a normal laptop when the required Python packages are installed. The evaluation script runs locally, requires no secret keys, and writes output to evaluation/results.json.

## 27. Files of interest
- src/pipeline.py: end-to-end pipeline wrapper
- src/intent_classifier.py: classifier and confidence logic
- src/retrieval.py: case retrieval
- src/reply_generator.py: grounded reply generation
- src/escalation.py: routing decision
- evaluation/run_evaluation.py: main evaluation entry point
- report/decision_log.md: engineering rationale
- data/golden_set.csv: evaluation dataset
