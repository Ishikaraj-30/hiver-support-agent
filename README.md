# AI Support Agent for @AmazonHelp

An automated customer support triage and response agent built for `@AmazonHelp` Twitter data using Retrieval-Augmented Generation (BM25 + Gemini 3.5 Flash Lite).

## Quickstart

1. Install dependencies:
   pip install -r requirements.txt

2. Set API key:
   $env:GEMINI_API_KEY="your-api-key"

3. Run benchmark:
   python scripts/run_evaluation.py

4. Interactive chat:
   python scripts/chat.py

## Key Results
- Dangerous False Auto-Handle: Reduced to 6.1% (vs 42.9% baseline).
- Escalation Accuracy: 48.9%
- LLM Judge Quality: 3.61 / 5.0

## Deliverables
- Detailed Analysis: REPORT.md
- Engineering Choices: decision_log.md
- Golden Evaluation Dataset: eval/golden_set.csv