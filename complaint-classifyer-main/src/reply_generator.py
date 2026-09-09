"""Grounded reply templates; retrieved historical language is evidence, not blind copy."""
TEMPLATES = {
    "billing_payment": "Sorry about the billing surprise. I can help review the charge and check whether a refund or credit applies. Please DM your mobile number and billing ZIP (never post account details publicly).",
    "account_access": "I can help get you back into your account. Please DM your mobile number and billing ZIP so our team can verify you securely and reset access.",
    "network_outage": "Sorry you are dealing with a service interruption. Please DM your location and mobile number so we can check for an outage and share the latest restoration update.",
    "slow_data": "Sorry your data is running slowly. Please DM your location, device model, and mobile number so we can check local coverage and your line.",
    "device_activation": "We can help activate the device or eSIM. Please DM your mobile number and device model, and we will check the activation status securely.",
    "plan_change": "I can help review plan options and any pricing impact. Please DM your mobile number and billing ZIP so we can look at the account securely.",
    "delivery_status": "I can check the order status. Please DM your order number and shipping ZIP (without posting personal details here), and we will look up the latest update.",
    "human_support": "I am sorry this has been frustrating. Please DM your mobile number and a short description of what happened so a specialist can review it securely.",
}

def generate_reply(intent, retrieved):
    base = TEMPLATES[intent]
    evidence = retrieved[0]["agent_response"] if retrieved else "No matching historical response was found."
    return {"reply": base, "evidence": evidence, "grounded": bool(retrieved)}
