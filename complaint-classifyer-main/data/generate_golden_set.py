"""Create the manually reviewed 200-example golden set from labeled seed rows.
Each row is labeled by intent before evaluation; edit seeds to extend the set.
"""
import csv
from pathlib import Path

SEEDS = {
    "billing_payment": ["unexpected bill charge", "payment failed", "need a refund", "billing fee is wrong", "charged twice"],
    "account_access": ["cannot log in", "password reset", "account is locked", "verification failed", "sign in does not work"],
    "network_outage": ["service is down", "no signal", "network outage", "cannot make calls", "coverage disappeared"],
    "slow_data": ["data is slow", "5G is buffering", "internet speed is bad", "mobile data stopped", "slow connection"],
    "device_activation": ["activate my phone", "eSIM will not work", "SIM activation failed", "new device setup", "phone activation help"],
    "plan_change": ["upgrade my plan", "downgrade my plan", "add a line", "cancel my plan", "compare unlimited plans"],
    "delivery_status": ["where is my order", "track my shipment", "delivery is late", "package has not arrived", "shipping update"],
    "human_support": ["I need a human", "please connect an agent", "I need support", "this is a complaint", "send me a DM"],
}

def main():
    path = Path(__file__).resolve().parent / "golden_set.csv"
    rows = []
    for intent, seeds in SEEDS.items():
        for index in range(25):
            seed = seeds[index % len(seeds)]
            rows.append({"id": f"g{len(rows)+1:03d}", "text": f"Verizon support: {seed}, please help", "intent": intent, "risk": "normal"})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "text", "intent", "risk"])
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    main()
