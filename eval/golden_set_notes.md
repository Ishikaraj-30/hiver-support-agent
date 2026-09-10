# Golden Evaluation Set Methodology

## 1. Scope & Dataset Sampling
- **Source**: Filtered from Kaggle's *Customer Support on Twitter* dataset specifically for brand `@AmazonHelp`.
- **Size**: 175 hand-curated and audited evaluation examples.
- **Stratification**: 25 balanced instances across 7 distinct operational intents:
  1. `order_tracking_delay`
  2. `return_refund`
  3. `account_payment_security`
  4. `damaged_defective_item`
  5. `subscription_digital`
  6. `service_complaint_frustration`
  7. `unsupported_language_or_noise`

## 2. Annotation & Ground-Truth Rules
Each tweet was labeled with:
1. `gold_intent`: Mutually exclusive operational bucket based on root cause rather than secondary sentiment.
2. `gold_escalate`: Boolean policy indicator:
   - `True` (Escalate to Human): Explicit account billing disputes, unauthorized charges, churn threats/escalated anger, foreign language inquiries, and missing refunds.
   - `False` (Auto-Handle Safe): Routine transit status queries, standard returns self-service, policy explanations, and replacement instructions.

## 3. Human vs. LLM-as-a-Judge Validation
- To validate the LLM Judge (`gemini-3.5-flash-lite`), a random sample of 25 agent-generated replies was independently hand-scored by human annotators across the 1–5 rubric (Groundedness, Tone, Safety).
- **Correlation**: Human vs. Judge scores demonstrated an **84% directional agreement** (Pearson $r = 0.78$), verifying that the automated judge serves as a trustworthy evaluation proxy.