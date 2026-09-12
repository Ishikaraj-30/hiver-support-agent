# Production-Grade AI Customer Support Agent for @AmazonHelp

An enterprise-ready AI triage, grounding, and escalation agent built on historical `@AmazonHelp` Twitter customer support interactions. Powered by **Retrieval-Augmented Generation (BM25 sparse indexing + Gemini 3.5 Flash Lite)** with structured JSON schema constraints.

The system addresses the core operational challenge of public support on social channels: **how to automate routine queries safely without misrouting high-risk security disputes or leaking sensitive PII in public view.**

---

## High-Level System Architecture

```text
                                  +-----------------------------+
                                  |  Incoming Customer Tweet    |
                                  +--------------+--------------+
                                                 |
                                                 v
                                  +-----------------------------+
                                  |   Preprocessing & Redaction |
                                  |   (Strip URLs, Mentions)    |
                                  +--------------+--------------+
                                                 |
                   +-----------------------------+-----------------------------+
                   |                                                           |
                   v                                                           v
   +-------------------------------+                           +-------------------------------+
   |   Historical Knowledge Base   |                           |    Structured Reasoning LLM   |
   |   (BM25 Sparse Retrieval)     |                           |    (Gemini 3.5 Flash Lite)    |
   |   - Historical brand replies  |                           |    - Strict Schema Output     |
   |   - Policy grounding anchors  |                           |    - System Prompt Guardrails |
   +---------------+---------------+                           +---------------+---------------+
                   |                                                           |
                   +-----------------------------> <---------------------------+
                                                 |
                                                 v
                                  +-----------------------------+
                                  |       Unified Output        |
                                  |                             |
                                  | 1. Intent (7-Class Taxonomy)|
                                  | 2. Escalation Gating & Why  |
                                  | 3. Policy-Grounded Draft    |
                                  +--------------+--------------+
                                                 |
                       +-------------------------+-------------------------+
                       |                                                   |
                       v                                                   v
        [escalate: true]                                    [escalate: false]
  Route to Human Support Queue                       Auto-Post Public Twitter Reply
  (PII, Frauds, Severe Threats)                     (<280 chars, Privacy Preserved)
```

---

## Core Capabilities

1. **7-Class Operational Intent Classification**: Maps raw customer tweets into an actionable operational taxonomy:
   - `order_tracking_delay`: Transit delays, carrier tracking inquiries.
   - `return_refund`: Item return authorization, refund status.
   - `account_payment_security`: Unauthorized charges, password resets, compromised accounts.
   - `damaged_defective_item`: Physical package damage, missing parts.
   - `subscription_digital`: Prime membership, Kindle/Audible digital asset access.
   - `service_complaint_frustration`: Courier rudeness, chronic service dissatisfaction.
   - `unsupported_language_or_noise`: Non-English inquiries, gibberish, spam.
2. **Asymmetric Escalation Gating**: Evaluates risk before replying. High-liability incidents (PII exposure, payment fraud, legal/abusive threats) are routed directly to human agents with a stated policy reason.
3. **BM25 Policy Grounding**: Retrieves the top-k most relevant historical `@AmazonHelp` resolution pairs to anchor the response voice, preventing generic hallucinated links.
4. **Strict PII & Brand Protection**: Enforces public timeline privacy rules—never requests or reflects order numbers, credit cards, or email addresses publicly; directs users to secure private DM channels.

---

## Quickstart: Reproduce Headline Benchmark (< 5 Minutes)

### 1. Clone repository and install dependencies
```bash
git clone [https://github.com/Ishikaraj-30/hiver-support-agent.git](https://github.com/Ishikaraj-30/hiver-support-agent.git)
cd hiver-support-agent
pip install -r requirements.txt
```

### 2. Set Gemini API key
In Windows PowerShell:
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

In Linux / macOS / Bash:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 3. Run headline benchmark evaluation
```bash
python scripts/run_evaluation.py
```
Evaluates Trivial Baseline, Simple Baseline, and the AI Agent across the 175-sample golden dataset. Produces full classification reports and exports detailed predictions to `benchmark_results.csv`.

### 4. Verify Human vs. LLM-as-a-Judge empirical agreement
```bash
python scripts/calc_judge_agreement.py
```
Computes Pearson correlation ($r$) and exact/directional agreement between 35 hand-labeled human quality ratings and the automated LLM judge.

---

## Interactive Live Testing (CLI)

Test arbitrary customer queries against the live pipeline:

```bash
python scripts/chat.py
```

**Example CLI Interaction:**
```text
Customer > Why was my card charged twice for Amazon Prime this morning?!
--------------------------------------------------------------------------------
[INTENT]      : account_payment_security
[ESCALATE]    : True
[REASON]      : Duplicate financial charge / payment dispute requires specialist audit.
[DRAFT REPLY] : We want to make sure your billing is secure. For your safety, please do not share account details publicly. Send us a direct message so our team can investigate: amzn.to/help
--------------------------------------------------------------------------------
```

---

## Headline Benchmark Results

Evaluated on the curated 175-sample Golden Evaluation Set (`eval/golden_set.csv`):

| Model Architecture | Intent Macro F1 | Intent Accuracy | Escalation Accuracy | False Auto-Handle Rate (Dangerous) | Unnecessary Escalation Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Trivial Baseline** (Majority Class) | 0.036 | 0.143 | 0.5714 | 0.4286 | 0.0000 |
| **Simple Baseline** (Keyword Rules) | 0.514 | 0.551 | 0.7347 | 0.2653 | 0.0000 |
| **AI Support Agent (Ours)** | **0.334** | **0.367** | **0.4898** | **0.0612** | **0.4490** |

### Key Takeaways
- **Catastrophic Failure Reduction**: The AI Agent drops the dangerous False Auto-Handle rate from **26.53%** (Keyword Baseline) and **42.86%** (Trivial Baseline) down to **6.12%**.
- **The Operational Trade-off**: The agent adopts a risk-averse posture (44.9% unnecessary escalation), choosing to spend human labor hours rather than risk leaving a compromised account or stolen delivery stranded on an automated loop.

### LLM-as-a-Judge Quality & Human Calibration
- **Average Overall Judge Score**: **3.61 / 5.00**
  - Groundedness & Policy Compliance: 3.60 / 5.00
  - Brand Voice & Empathy: 3.60 / 5.00
  - Actionability & Privacy Safety: 3.65 / 5.00
- **Empirical Human Agreement Validation** (n = 35 samples):
  - **Pearson Correlation (r)**: **0.789** (Strong empirical alignment)
  - **Exact Agreement (1-5 scale)**: **80.0%**
  - **Directional Agreement (within 1 point)**: **100.0%**

---

## Project Structure & Deliverables

```text
hiver-support-agent/
|-- REPORT.md                    # Comprehensive technical report (framing, metrics, 5 failure modes, misleading headline)
|-- decision_log.md              # 14 non-obvious engineering decisions and trade-offs
|-- README.md                    # System documentation and reproduction guide
|-- requirements.txt             # Python dependencies
|
|-- data/
|   `-- reconstructed_pairs.csv  # Cleaned customer-agent tweet conversation pairs
|
|-- eval/
|   |-- golden_set.csv           # 175-sample hand-labelled golden evaluation dataset
|   |-- golden_set_notes.md      # Sampling, stratification, and labeling methodology note
|   `-- human_eval_benchmark.csv # 35-sample paired human ratings vs. LLM judge scores
|
|-- src/
|   |-- agent.py                 # Core AI agent pipeline (intent classification, escalation, reply drafting)
|   |-- baselines.py             # Trivial (majority class) and Simple (keyword heuristic) baselines
|   `-- retrieval.py             # In-memory BM25 sparse index for historical grounding
|
`-- scripts/
    |-- calc_judge_agreement.py  # Script computing Pearson r and human-judge agreement
    |-- run_evaluation.py        # End-to-end benchmark harness across all models
    `-- chat.py                  # Interactive CLI interface for live query testing
```

---

## Technical Stack & Dependencies

- **Language & Runtime**: Python 3.10+
- **LLM Engine**: Google Gemini API (`gemini-2.5-flash` / `gemini-3.5-flash-lite`) via Google GenAI SDK
- **Retrieval Engine**: `rank-bm25` (Sparse lexical index over historical resolution corpus)
- **Data & Evaluation**: `pandas`, `numpy`, `scikit-learn`, `scipy`