import json
import re
import time
import google.generativeai as genai


class AmazonSupportAgent:

  def __init__(self, api_key: str, retriever, model='gemini-3.5-flash-lite'):
    genai.configure(api_key=api_key)
    self.model = genai.GenerativeModel(model)
    self.retriever = retriever

  def predict(self, tweet: str):
    retrieved = self.retriever.query(tweet, top_k=2)
    grounding = '\n'.join(
        [f"- Past Resolution: {r['brand_reply']}" for r in retrieved]
    )

    prompt = f"""You are an expert AI customer support agent for @AmazonHelp on Twitter.
Tasks:
1. Classify the customer tweet into EXACTLY ONE intent:
   [order_tracking_delay, return_refund, account_payment_security, damaged_defective_item, subscription_digital, service_complaint_frustration, unsupported_language_or_noise]
2. Decide whether to ESCALATE (true) or AUTO-HANDLE (false):
   - Escalate (true) if: account security/passwords/charges/2FA, anger/severe complaint/churn risk, non-English tweets, or unresolved missing refunds.
   - Auto-handle (false) if: routine tracking, standard return self-service steps, replacement steps, Prime membership self-service.
3. State a 1-sentence policy reason.
4. Draft a grounded reply under 280 characters. Never ask for private info (order ID, email, card) publicly; direct to DM if private lookup is needed.

Customer Tweet: "{tweet}"

Historically Resolved Reference Replies for similar issues:
{grounding}

Respond ONLY with valid JSON:
{{
  "intent": "<intent_name>",
  "escalate": true,
  "reason": "<one sentence>",
  "reply": "<draft under 280 chars>"
}}"""

    for attempt in range(3):
      try:
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type='application/json', temperature=0.0
            ),
        )
        text = response.text.strip()
        return json.loads(text)
      except Exception as e:
        if attempt < 2:
          time.sleep(2 * (attempt + 1))
          continue
        return {
            'intent': 'service_complaint_frustration',
            'escalate': True,
            'reason': f'Error: {e}',
            'reply': (
                'Please send us a direct message so we can assist you right'
                ' away.'
            ),
        }
