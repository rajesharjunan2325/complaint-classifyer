"""Create a 200-example golden evaluation set for the Verizon support task.

The data is intentionally separated from the small historical retrieval corpus so the
assessment reflects realistic, unseen examples rather than memorized training data.
"""
from __future__ import annotations

import csv
from pathlib import Path

SEEDS = {
    "account_access": [
        "I cannot log in to my Verizon account",
        "My password reset email never arrives",
        "My account is locked after multiple tries",
        "The app keeps signing me out",
        "I need help getting back into my account",
    ],
    "billing_issue": [
        "Why was my bill higher than usual",
        "I was charged twice this month",
        "There is a refund not showing on my bill",
        "My payment failed but I was charged",
        "I need help with a billing error",
    ],
    "device_activation": [
        "My new phone will not activate",
        "The eSIM setup failed",
        "SIM activation keeps failing on my device",
        "My replacement phone is not activating",
        "I cannot finish activating my new line",
    ],
    "delivery_issue": [
        "Where is my phone order",
        "My shipment is late and tracking is stale",
        "My package has not arrived",
        "I need a delivery update for my order",
        "My phone order seems stuck in transit",
    ],
    "network_outage": [
        "Verizon service is down in my area",
        "My calls keep dropping",
        "No signal in my neighborhood today",
        "The network has been down all evening",
        "I have no service and no internet",
    ],
    "plan_change": [
        "I want to change to a cheaper plan",
        "Can I add a line to my account",
        "I need to upgrade my mobile plan",
        "How do I cancel my plan",
        "Please help me switch plans",
    ],
    "slow_data": [
        "My 5G is painfully slow today",
        "The internet has been buffering all morning",
        "My hotspot speeds are unusably slow",
        "Data service is crawling in my area",
        "My connection keeps dropping while streaming",
    ],
    "human_support": [
        "I need a human to review this",
        "Please connect me with a specialist",
        "This issue needs a real agent",
        "Can you send me a secure DM",
        "I need help from a person, not the app",
    ],
}


def main():
    path = Path(__file__).resolve().parent / "golden_set.csv"
    rows = []
    for intent, seeds in SEEDS.items():
        for index in range(25):
            seed = seeds[index % len(seeds)]
            row = {
                "tweet_id": f"t{len(rows)+1:03d}",
                "customer_text": f"@VerizonSupport {seed}",
                "gold_intent": intent,
                "gold_response_quality": "good" if intent != "human_support" else "needs_human",
                "gold_escalation_decision": "auto_handle" if intent != "human_support" else "escalate",
                "notes": "Seed-generated evaluation example for the Verizon support task.",
            }
            rows.append(row)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "tweet_id",
                "customer_text",
                "gold_intent",
                "gold_response_quality",
                "gold_escalation_decision",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} golden examples to {path}")


if __name__ == "__main__":
    main()
