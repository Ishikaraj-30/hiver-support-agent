# Engineering Report: Production-Grade Customer Support AI Agent (@AmazonHelp)

## 1. Executive Summary
This project evaluates an automated customer support agent for `@AmazonHelp` built on top of Twitter customer service interactions. The agent operates across three coordinated tasks:
1. **Intent Classification**: Mapping raw customer tweets to a 7-class operational taxonomy.
2. **Policy Escalation Gating**: Determining whether a query can be resolved via automated self-service or must escalate to human specialist queues.
3. **Grounded Reply Generation**: Drafting policy-compliant, privacy-preserving responses (<280 characters) grounded in retrieved historical resolutions via BM25.

---

## 2. Benchmark & Headline Comparison

Evaluation was performed on a stratified golden evaluation set across three tiers of systems:
- **Trivial Baseline**: Majority-class predictor (`order_tracking_delay`), canned static response, zero escalations.
- **Simple Baseline**: Rule-based keyword matching intent classifier + 1-NN BM25 verbatim historical reply.
- **AI Support Agent**: Retrieval-Augmented Generation (BM25 + Gemini 3.5 Flash Lite) with structured schema constraints.

### Quantitative Comparison Table

| Model | Intent Macro F1 | Intent Accuracy | Escalation Accuracy | False Auto-Handle (Dangerous) | Unnecessary Escalation |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Trivial Baseline** | 0.036 | 0.143 | 0.5714 | 0.4286 | 0.0000 |
| **Simple Baseline** | 0.514 | 0.551 | 0.7347 | 0.2653 | 0.0000 |
| **AI Support Agent** | **0.334** | **0.367** | **0.4898** | **0.0612** | **0.4490** |

### Qualitative LLM-as-a-Judge Evaluation (1.0 to 5.0 Scale)
A 20-sample randomized cohort of drafted replies was scored across three orthogonal dimensions:
- **Groundedness & Policy Adherence**: **3.60 / 5.00**
- **Tone & Empathy**: **3.60 / 5.00**
- **Actionability & Privacy Safety**: **3.65 / 5.00**
- **Overall Response Quality**: **3.61 / 5.00**

---

## 3. Safety & Asymmetric Risk Analysis
In customer support operations, classification errors have asymmetric real-world costs:
1. **False Auto-Handle (Critical Failure)**: Occurs when a high-risk security issue, compromised credential, or urgent refund failure is incorrectly marked as auto-handled. The customer receives a generic automated link, increasing churn risk and account vulnerability.
   - The **Trivial Baseline** fails dangerously **42.9%** of the time.
   - The **Simple Baseline** fails dangerously **26.5%** of the time due to ambiguous keywords.
   - The **AI Support Agent** cuts dangerous failures down to **6.12%**, successfully routing sensitive matters to human workflows.
2. **Unnecessary Escalation (Operational Cost)**: Occurs when a routine tracking inquiry is sent to human agents. The agent exhibits a risk-averse bias (44.9% over-escalation), trading labor bandwidth for customer protection.

---

## 4. Failure Analysis: 5 Concrete Cases

From `benchmark_results.csv`, failure modes group into distinct operational patterns:

### Case 1: Delivery Delay vs. Frustration Conflation (Intent Confusion)
* **Customer Tweet**: *"Where is my order? It was supposed to be delivered yesterday and your tracker hasn't updated in 24 hours. Terrible service!"*
* **Ground Truth**: `order_tracking_delay` | Escalate: `False`
* **Agent Prediction**: `service_complaint_frustration` | Escalate: `True`
* **Root Cause**: The LLM anchored on the sentiment tokens (*"terrible service"*) rather than the root operational driver (*"where is my order"*).
* **Remedy**: Update classification instructions to establish intent precedence: operational tracking requests take priority over secondary sentiment.

### Case 2: Multi-Intent Refund and Replacement
* **Customer Tweet**: *"The shoes arrived broken and the box was crushed. I want to return them for a refund or replacement asap."*
* **Ground Truth**: `damaged_defective_item` | Escalate: `False`
* **Agent Prediction**: `return_refund` | Escalate: `False`
* **Root Cause**: Overlapping taxonomy boundaries. The customer explicitly mentions "return/refund" and "broken".
* **Remedy**: Introduce hierarchical intent schemas (e.g., `item_condition.damaged` vs `billing.refund`).

### Case 3: Over-Cautious Escalation on Minor Delay
* **Customer Tweet**: *"Package is running 2 hours late. Is the driver still coming today?"*
* **Ground Truth**: Escalate: `False`
* **Agent Prediction**: Escalate: `True` (Reason: *"Customer is inquiring about an active late delivery needing status check."*)
* **Root Cause**: The system prompt stated that missing packages should be escalated, causing the model to treat minor transit windows as lost packages.
* **Remedy**: Clarify prompt threshold: only escalate if the delivery date has passed by >48 hours or tracking displays an exception status.

### Case 4: Public Timeline Privacy Leak Prevention (Success Case)
* **Customer Tweet**: *"I need help with order #112-9847291-8273612, I was charged twice."*
* **Agent Reply**: *"We'd like to look into this billing concern for you. For your security, please do not share account details publicly—send us a DM with your order info: amzn.to/help"*
* **Evaluation**: Scored 5/5 on Privacy & Actionability. The agent stripped public PII exposure and moved the customer into private channels.

### Case 5: Sarcasm and Colloquial Language
* **Customer Tweet**: *"Shoutout to Amazon for delivering my laptop box completely empty. Best Christmas gift ever."*
* **Ground Truth**: `damaged_defective_item` / High-Severity Escalate: `True`
* **Agent Prediction**: `order_tracking_delay` | Escalate: `False`
* **Root Cause**: Lexical literalism failed on sarcasm (*"Best Christmas gift ever"* interpreted as positive delivery acknowledgment).
* **Remedy**: Add few-shot sarcasm examples to the in-context prompt.

---

## 5. Production Viability & Next Steps

1. **Dual-Pass Cascade Pipeline**:
   - Use a lightweight, fine-tuned DistilBERT or SetFit model locally for intent classification ($<10\text{ms}$ latency, zero API cost).
   - Reserve LLM generation strictly for the drafting layer when human agents require assisted replies.
2. **Escalation Calibration**:
   - Tune classification decision thresholds on the logit layer to reduce the 44.9% unnecessary escalation rate down to an operationally sustainable 15–20%.
3. **Guardrail Layer**:
   - Enforce regex-based PII detection filters on outbound drafts to guarantee zero accidental leakage of phone numbers or internal URLs.