# Decision log

| # | Decision | Reason |
|---|---|---|
| 1 | Use Verizon as the single brand | Keeps language, policies, and historical evidence coherent. |
| 2 | Define eight intents | Covers common support journeys without making labels too granular. |
| 3 | Keep classifier deterministic | Makes the submission reproducible offline and exposes failure modes. |
| 4 | Retrieve only Verizon historical responses | Replies need brand-specific evidence. |
| 5 | Ask for a secure DM, never public account data | Twitter is a public channel. |
| 6 | Escalate low confidence | A wrong confident answer is higher risk than a handoff. |
| 7 | Escalate fraud, legal, safety, and urgent language | These cases need policy-aware human judgment. |
| 8 | Use templates informed by retrieval | Prevents unsupported promises while retaining a helpful tone. |
| 9 | Include a trivial majority baseline | Establishes the minimum useful benchmark. |
| 10 | Include a keyword baseline | Measures the gain over the existing project’s approach. |
| 11 | Score replies on relevance, safety, actionability, empathy | Captures quality beyond intent accuracy. |
| 12 | Manually review 20 replies | Small, explicit audit set supports agreement measurement. |
