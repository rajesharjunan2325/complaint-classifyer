# Verizon Support Agent Report

## Brand and dataset
The project focuses on Verizon support conversations in the Customer Support on Twitter dataset. Verizon was selected because it has a consistent set of recurring issues, strong social support language, and enough historical support examples to support retrieval-based grounding.

## Intent taxonomy
The system targets these intents:

- account_access
- billing_issue
- device_activation
- delivery_issue
- network_outage
- plan_change
- slow_data
- human_support

## Pipeline
The model pipeline performs preprocessing, intent classification, confidence scoring, historical retrieval, grounded reply generation, and escalation.

## Evaluation status
The repository includes scripts to generate the golden set and calculate evaluation metrics. The results are written to evaluation/results.json after running the evaluation script.

## What is misleading about my headline number?
### What is misleading about my headline number?
A headline number can be misleading because a single metric hides class imbalance, retrieval weakness, limited labeled examples, and poor calibration. Real support tasks also require trustworthy escalation decisions and grounded replies, not just a good accuracy score.

## One-week next steps
1. Improve the difficult overlap classes
2. Improve retrieval quality
3. Calibrate escalation thresholds
4. Strengthen response grounding
5. Expand evaluation data and human review

## Failure analysis summary
The main failure modes are overlapping support intents, underspecified language, missing historical evidence, unsafe public data requests, and high-risk or urgent content that should be routed to a person.

## Decision log
The full engineering decision log is available in report/decision_log.md.
