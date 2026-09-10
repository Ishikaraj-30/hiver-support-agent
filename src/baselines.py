class TrivialBaseline:

  def predict(self, tweet):
    return {
        "intent": "order_tracking_delay",
        "reply": (
            "Hi there! We are sorry for any delay. You can check the latest"
            " status of your package anytime under 'Your Orders' on the Amazon"
            " app."
        ),
        "escalate": False,
        "reason": (
            "Trivial baseline default: always order_tracking_delay and"
            " auto-handle."
        ),
    }


class SimpleBaseline:

  def __init__(self, retriever):
    self.retriever = retriever
    self.keywords = {
        "account_payment_security": [
            "charge",
            "fraud",
            "unauthorized",
            "locked",
            "password",
            "otp",
            "card",
        ],
        "damaged_defective_item": [
            "broken",
            "damaged",
            "shattered",
            "expired",
            "wrong item",
        ],
        "return_refund": ["refund", "return", "drop off", "money back"],
        "subscription_digital": ["prime", "kindle", "audible", "membership"],
        "service_complaint_frustration": [
            "worst",
            "terrible",
            "horrible",
            "scam",
            "driver",
            "useless",
        ],
        "order_tracking_delay": [
            "track",
            "where",
            "late",
            "delay",
            "package",
            "deliver",
        ],
    }

  def predict(self, tweet):
    tweet_lower = str(tweet).lower()
    selected_intent = "order_tracking_delay"
    for intent, kws in self.keywords.items():
      if any(kw in tweet_lower for kw in kws):
        selected_intent = intent
        break

    escalate = selected_intent in [
        "account_payment_security",
        "service_complaint_frustration",
    ]
    retrieved = self.retriever.query(tweet, top_k=1)
    reply = (
        retrieved[0]["brand_reply"][:270]
        if retrieved
        else "Please reach out to our customer support team for assistance."
    )

    return {
        "intent": selected_intent,
        "reply": reply,
        "escalate": escalate,
        "reason": "Keyword pattern matched.",
    }