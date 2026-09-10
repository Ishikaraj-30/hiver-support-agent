# Engineering Decision Log

1. **Brand Selection (@AmazonHelp)**: Selected due to high volume, established self-service customer journeys, and clear separation between automated tasks (package status) and human tasks (fraud/account locks).
2. **Intent Granularity (7 Intents)**: Derived empirically from clustering actual conversation topics rather than using generic customer service schemas.
3. **BM25 Retrieval over Embeddings**: Chose in-memory BM25 to guarantee deterministic, sub-second indexing without requiring external vector database infrastructure or GPU overhead.
4. **Explicit Language/Noise Class**: Routed non-English tweets to `unsupported_language_or_noise` to escalate to regional queues rather than risking inaccurate auto-translation.
5. **Asymmetric Escalation Cost**: In safety metrics, False Auto-Handle is treated as a critical security/policy violation, whereas Unnecessary Escalation is treated as an operational efficiency cost.
6. **Strict 280-Character Budget**: All drafted replies enforce Twitter's character constraint to mirror production constraints.
7. **Prohibition on Public PII Requests**: The prompt strictly instructs the agent never to ask for account credentials, order IDs, or phone numbers in public tweets, routing authenticated inquiries directly to Direct Messages.
8. **Few-Shot In-Context Grounding**: Top-2 historical resolutions retrieved via BM25 are injected directly into the LLM system prompt to prevent hallucination of policies or refund windows.
9. **Zero Temperature on Categorization & Gating**: Maintained 0.0 temperature for deterministic, audit-traceable classification and escalation decisions.
10. **Stratified Sampling of Golden Set**: Prevented delivery queries from dominating evaluation by setting quota targets across all 7 intents.