"""Grounded reply generation that ties the answer back to historical Verizon support responses."""
from __future__ import annotations

TEMPLATES = {
    "billing_issue": "Sorry about the billing surprise. I can help review the charge and check whether a credit or adjustment applies. Please DM your mobile number and billing ZIP so we can look at the account securely.",
    "account_access": "I can help get you back into your account. Please DM your mobile number and billing ZIP so our team can verify you securely and reset access.",
    "network_outage": "Sorry you are dealing with a service interruption. Please DM your location and mobile number so we can check for an outage and share the latest restoration update.",
    "slow_data": "Sorry your data is running slowly. Please DM your location, device model, and mobile number so we can check local coverage and your line.",
    "device_activation": "We can help activate the device or eSIM. Please DM your mobile number and device model, and we will check the activation status securely.",
    "plan_change": "I can help review plan options and any pricing impact. Please DM your mobile number and billing ZIP so we can look at the account securely.",
    "delivery_issue": "I can check the order status. Please DM your order number and shipping ZIP, and we will look up the latest update.",
    "human_support": "I am sorry this has been frustrating. Please DM your mobile number and a short description of what happened so a specialist can review it securely.",
}


def generate_reply(intent, retrieved, customer_text=None):
    base = TEMPLATES.get(intent, TEMPLATES["human_support"])
    evidence = []
    if retrieved:
        for item in retrieved:
            evidence.append({
                "customer_message": item.get("customer_message", ""),
                "agent_response": item.get("agent_response", ""),
                "similarity": item.get("similarity", 0.0),
            })
    else:
        evidence = [{"customer_message": customer_text or "", "agent_response": "No directly matching historical response found.", "similarity": 0.0}]
    return {
        "reply": base,
        "evidence": evidence,
        "grounded": bool(retrieved),
    }
