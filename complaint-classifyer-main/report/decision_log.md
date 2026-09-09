# Decision log

1. Decision: Use Verizon as the single-brand target.
   Why: A single brand reduces noisy language and keeps the retrieval evidence consistent.
   Alternatives considered: Multi-brand rendition or all public support tweets.
   Evidence: The dataset contains recurring patterns across Verizon support conversations that are easier to model in a single slice.
   Trade-off: This reduces generality but improves retrieval quality and grounding.

2. Decision: Define eight intents instead of a large raw label set.
   Why: It captures the main customer journeys without creating an unstable taxonomy.
   Alternatives considered: Very granular labels or a broad "other" bucket.
   Evidence: The historical data is dominated by account, billing, data, activation, delivery, and human-support needs.
   Trade-off: Some edge cases will still overlap, but the taxonomy remains practical.

3. Decision: Use a lightweight TF-IDF + Linear SVC classifier.
   Why: It is fast, transparent, and reliable on short texts.
   Alternatives considered: Large transformer models and regex-only classification.
   Evidence: A compact classifier performs well on short support interactions and is easy to reproduce locally.
   Trade-off: It is less expressive than larger language models for rare edge cases.

4. Decision: Keep the preprocessing simple and deterministic.
   Why: Support conversations are short and noisy; normalization is enough.
   Alternatives considered: Extensive text augmentation or heavy NLP cleaning.
   Evidence: Standard lowercasing, URL stripping, punctuation cleanup, and tokenization are sufficient for the task.
   Trade-off: Rare lexical variants may need more explicit handling later.

5. Decision: Base replies on historical support examples rather than free-form generation.
   Why: Grounded responses are safer and better aligned with brand behavior.
   Alternatives considered: Prompt-only generation with no evidence.
   Evidence: Historical Verizon responses consistently ask for secure DM handoff and issue verification.
   Trade-off: The replies are less creative but much safer.

6. Decision: Use retrieval similarity to select historical examples.
   Why: Similar historical cases provide stronger justification than a generic template.
   Alternatives considered: Keyword-matching only or no retrieval.
   Evidence: Similar customer messages and their agent responses act as the evidence chain for the response.
   Trade-off: Retrieval quality is still modest for novel or sparse issues.

7. Decision: Set escalation thresholds based on confidence and retrieval similarity.
   Why: Auto-handle should only be used when the system has a clear signal.
   Alternatives considered: Always auto-handle when the intent is known.
   Evidence: Low-confidence or low-similarity cases are more likely to produce weak or unsupported replies.
   Trade-off: More cases are escalated than a purely aggressive auto-handle policy.

8. Decision: Escalate urgent or risky language immediately.
   Why: Public support channels are not appropriate for fraud, legal, or safety issues.
   Alternatives considered: Attempt to answer without escalation.
   Evidence: The historical dataset and assignment framework both call for secure DM handoff for sensitive issues.
   Trade-off: This may reduce automation for a subset of cases.

9. Decision: Include explicit baseline metrics.
   Why: A baseline shows whether the system is meaningfully better than trivial behavior.
   Alternatives considered: Reporting only the final model.
   Evidence: This is required by the assignment and helps explain model gains.
   Trade-off: Baselines can be intentionally weak but are necessary for honest comparison.

10. Decision: Use a small golden set instead of training on it.
   Why: It keeps the evaluation independent from the model development process.
   Alternatives considered: Mixing evaluation examples into the training set.
   Evidence: The assignment explicitly requires avoiding leakage between evaluation and training/retrieval.
   Trade-off: The evaluation sample is smaller and may be less representative.

11. Decision: Keep the judge offline and explicit.
   Why: The repo needs to remain runnable without API keys.
   Alternatives considered: Hard-coded model calls or secret-laden configuration.
   Evidence: The environment may not have an API key, and the assignment asks for a local/mock option.
   Trade-off: The judge is simpler than a hosted LLM judge and has more explicit limitations.

12. Decision: Include human agreement checking.
   Why: Even a simple agreement metric helps estimate whether judge scoring is stable.
   Alternatives considered: Reporting only automated metrics.
   Evidence: A small subset of human review is enough to expose disagreement patterns.
   Trade-off: Human evaluation samples are necessarily small and limited.

13. Decision: Keep the repository modular and simple.
   Why: A reproducible project should be easy to inspect and run.
   Alternatives considered: A monolithic notebook or opaque script.
   Evidence: The assignment stresses readability, modularity, and reproducibility.
   Trade-off: The implementation is intentionally lightweight rather than feature-rich.

14. Decision: Document the limitations directly in the repo.
   Why: Reviewers should know where the system is safe, where it can fail, and what is not yet production-ready.
   Alternatives considered: Only reporting happy-path results.
   Evidence: The assignment explicitly asks for failure analysis and a “headline number” discussion.
   Trade-off: This may make the project appear less polished, but it is more honest and defensible.
