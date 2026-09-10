import re
import pandas as pd

INTENT_RULES = {
    "account_payment_security": [
        r"charge",
        r"fraud",
        r"unauthoriz",
        r"locked",
        r"password",
        r"otp",
        r"hacked",
        r"gift card",
        r"credit card",
        r"billing",
    ],
    "service_complaint_frustration": [
        r"worst",
        r"terrible",
        r"ridiculous",
        r"driver",
        r"horrible",
        r"scam",
        r"unacceptable",
        r"disgust",
        r"lawsuit",
        r"rude",
    ],
    "damaged_defective_item": [
        r"broken",
        r"damaged",
        r"shattered",
        r"defect",
        r"wrong item",
        r"expired",
        r"missing",
        r"leaking",
    ],
    "return_refund": [
        r"refund",
        r"return",
        r"exchange",
        r"money back",
        r"drop off",
        r"drop-off",
        r"ups",
    ],
    "subscription_digital": [
        r"prime",
        r"kindle",
        r"audible",
        r"prime video",
        r"membership",
        r"subscription",
        r"music",
    ],
    "order_tracking_delay": [
        r"track",
        r"deliver",
        r"late",
        r"where is",
        r"package",
        r"arrived",
        r"transit",
        r"eta",
        r"status",
    ],
}

ESCALATION_REASONS = {
    "account_payment_security": "Requires private account access and identity verification; high security/PII risk.",
    "service_complaint_frustration": "Severe negative sentiment and churn risk; requires human de-escalation via private DM.",
    "unsupported_language_or_noise": "Non-English message or noisy fragment; requires specialized language routing or triage.",
    "damaged_defective_item": "Standard replacement/return can be self-served through 'Your Orders' > 'Return or Replace Items'.",
    "order_tracking_delay": "Tracking progress can be self-served through 'Your Orders' tracking portal.",
    "return_refund": "Standard return/refund policies and drop-off guidance can be self-served via customer portal.",
    "subscription_digital": "Membership cancellations and digital settings can be self-served under 'Manage Your Prime Membership'.",
}


def classify_intent(text: str) -> str:
    # 1. Non-English / Foreign character check
    non_ascii_count = sum(1 for ch in text if ord(ch) > 127)
    if non_ascii_count > max(len(text) * 0.15, 6):
        return "unsupported_language_or_noise"

    text_lower = text.lower()

    # 2. Check prioritized intents
    for intent, patterns in INTENT_RULES.items():
        if any(re.search(pat, text_lower) for pat in patterns):
            return intent

    return "service_complaint_frustration"


print("Reading reconstructed_pairs.csv...")
df = pd.read_csv("reconstructed_pairs.csv").dropna(
    subset=["customer_text", "brand_text"]
)

# Apply classification heuristic
df["intent"] = df["customer_text"].apply(classify_intent)

# Define balanced target distribution across the 7 intents
targets = {
    "order_tracking_delay": 35,
    "return_refund": 30,
    "damaged_defective_item": 25,
    "account_payment_security": 25,
    "service_complaint_frustration": 25,
    "subscription_digital": 20,
    "unsupported_language_or_noise": 15,
}

sampled_batches = []
for intent, count in targets.items():
    subset = df[df["intent"] == intent]
    n_sample = min(count, len(subset))
    sampled_batches.append(subset.sample(n=n_sample, random_state=42))

golden_df = pd.concat(sampled_batches).reset_index(drop=True)

# Build standard golden schema
golden_df["gold_intent"] = golden_df["intent"]
golden_df["gold_escalate"] = golden_df["gold_intent"].isin(
    [
        "account_payment_security",
        "service_complaint_frustration",
        "unsupported_language_or_noise",
    ]
)
golden_df["gold_escalate_reason"] = golden_df["gold_intent"].map(
    ESCALATION_REASONS
)

# Clean up column selection
output_cols = [
    "thread_id",
    "customer_text",
    "gold_intent",
    "gold_escalate",
    "gold_escalate_reason",
    "brand_text",
]
final_golden = golden_df[output_cols].rename(
    columns={"customer_text": "customer_tweet", "brand_text": "reference_reply"}
)

out_path = "golden_set.csv"
final_golden.to_csv(out_path, index=False, encoding="utf-8")
print(f"Created {len(final_golden)} golden evaluation examples in {out_path}!")
print("\nIntent distribution in golden set:")
print(final_golden["gold_intent"].value_counts())
print("\nEscalation breakdown:")
print(final_golden["gold_escalate"].value_counts())