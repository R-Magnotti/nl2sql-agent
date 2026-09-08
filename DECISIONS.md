## Direct API calls instead of LangChain

**Context:** Small pipeline, one model, one retrieval step. Ollama already exposes an OpenAI-compatible endpoint.
**Options considered:** LangChain, LlamaIndex, plain Python with direct calls.
**Decision:** Plain Python, direct calls to the endpoint.
**Why:** The system's small enough to own every layer. Debugging my own code beats stepping through framework internals, and I skip the dependency churn.
**Tradeoffs:** I rebuild small things a framework gives for free, templating, retries. With many models or tools in play I'd revisit.

## Model choice for query-column inferencing
**Context:** Given a user query, we want to compare it to column names to find the best match (or no match). 
**Options considered:** Small language models like qwen3, gemma3, phi4, etc. 
**Decision:** 
**Why:** Ran cross comparison of some of these models, and selected highest performing on test cases.
**Tradeoffs:** 



