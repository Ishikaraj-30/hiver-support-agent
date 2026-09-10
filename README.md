content = """# AI Customer Support Agent for @AmazonHelp

An end-to-end AI triage and response agent built for `@AmazonHelp` Twitter customer support using Retrieval-Augmented Generation (BM25 + Gemini 3.5 Flash Lite).

The agent handles three coordinated tasks per incoming tweet:
1. **Intent Classification**: Classifies into a 7-class operational taxonomy.
2. **Escalation Gating**: Decides whether to auto-handle or escalate to human specialists with a stated policy reason.
3. **Grounded Reply Generation**: Drafts policy-compliant, privacy-safe responses (<280 characters) grounded in historical resolution data.

---

## Quickstart: Reproduce Headline Benchmark (< 5 Minutes)

### 1. Clone repository and install dependencies
```bash
git clone [https://github.com/Ishika-29-raj/hiver-support-agent.git](https://github.com/Ishika-29-raj/hiver-support-agent.git)
cd hiver-support-agent
pip install -r requirements.txt