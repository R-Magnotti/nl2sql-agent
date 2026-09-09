## Direct API calls instead of LangChain

***Context:**** Small pipeline, one model, one retrieval step. Ollama already exposes an OpenAI-compatible endpoint.
**Options considered:** LangChain, LlamaIndex, plain Python with direct calls.
**Decision:** Plain Python, direct calls to the endpoint.
**Why:** The system's small enough to own every layer. Debugging my own code beats stepping through framework internals, and I skip the dependency churn.
**Tradeoffs:** I rebuild small things a framework gives for free, templating, retries. With many models or tools in play I'd revisit.

## Model choice for query-column inferencing
**Context:** Given a query term, decide which warehouse column answers it, that none does, or that two readings are equally valid and the agent should ask. Labels: clear / ambiguous / refuse.
**Options considered:** Over the same 41 cases: three embedders reading a verdict off cosine gaps against fitted thresholds (all-MiniLM-L6-v2, Qwen3-Embedding-0.6B, Qwen3-Embedding-4B), and four prompted judges labelling the column pair directly (qwen3:0.6b, qwen3:4b, qwen3:4b-instruct, gemma3:4b). Each with bare column names and with names plus descriptions.
**Decision:** qwen3:4b, prompted, with descriptions. 33/41.
**Why:** Top of the table (evals\reports\test_retrieval_out.txt), and the only judge well clear of the majority baseline -- always answering CLEAR scores 21/41. The best embedder is level at 32/41, but its `GAP` and `clear_floor` are fitted on these same 41 cases while the judge has no fitted parameters, so only one of those two numbers is held out. Refuse is 8/8 against the best embedder's 5/8. gemma3:4b landed below the baseline; qwen3:0.6b and 4b-instruct sat inside noise of it.
**Tradeoffs:** Weakest among all categories, on ambiguous at 6/12, and all six misses come back CLEAR -- it picks a grain the user never specified rather than asking, which is the costly error here. `name_only` is a shade safer on that class (7/12) for two points less overall. Costs a generation per decision instead of a dot product (i.e. embedding models), plus a running ollama server. With 41 cases anything inside ±2 is noise, so this is directional. The bet is that a prompt transfers across schemas where a threshold is refit per warehouse.



