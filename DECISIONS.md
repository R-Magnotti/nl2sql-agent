## 📝 Direct API calls instead of LangChain for LLM Inference
**Context:** Small pipeline, one model, one retrieval step. Ollama already exposes an OpenAI-compatible endpoint.
**Options considered:** LangChain, LlamaIndex, plain Python with direct calls.
**Decision:** Plain Python, direct calls to the endpoint.
**Why:** The system's small enough to own every layer. Debugging my own code beats stepping through framework internals, and I skip the dependency churn.
**Tradeoffs:** I rebuild small things a framework gives for free, templating, retries. With many models or tools in play I'd revisit.

## 📝 Model choice for query-column inferencing 
**Context:** Given a query term, decide which warehouse column answers it, that none does, or that two readings are equally valid and the agent should ask a clarification question. Labels: `CLEAR` / `AMBIGUOUS` / `REFUSE`.
**Options considered:** Over the same 41 cases: three embedders reading a verdict off cosine gaps against fitted thresholds (all-MiniLM-L6-v2, Qwen3-Embedding-0.6B, Qwen3-Embedding-4B), and four prompted judges labelling the column pair directly (qwen3:0.6b, qwen3:4b, qwen3:4b-instruct, gemma3:4b). Each with bare column names and with names plus descriptions.
**Decision:** qwen3:4b, prompted, with descriptions. 33/41.
**Why:** Top of the table (evals/reports/test_retrieval_out.txt), and the only judge well clear of the majority baseline -- always answering `CLEAR` scores 21/41. The best _embedder_ is about the same performance at 32/41, but its gating thresholds (`GAP` and `clear_floor`) are fitted on these same 41 cases while the judge has no fitted parameters, so only one of those two numbers is held out. `REFUSE` is 8/8 against the best embedder's 5/8. gemma3:4b landed below the baseline; qwen3:0.6b and 4b-instruct were close to the baseline.
**Tradeoffs:** Weakest among all categories, on `AMBIGUOUS` for qwen3:4b at 6/12, and all six misses come back `CLEAR` -- it guesses which column the user meant instead of asking, which is the costly error here. `name_only` is a little bit safer on that class (7/12) for two points less in total across all examples and categories. Costs a generation per decision instead of a dot product (i.e. embedding models), plus a running ollama server. With 41 cases anything inside ±2 is noise, so this is directional. The bet is that a prompt transfers across schemas where a threshold is refit per warehouse.

## 📝 Two-stage ambiguity layer for RAG agent: retrieve, then judge
**Context:** Manually dumping every column into the prompt doesn't scale when businesses could have thousands of columns or more. This entry is the architecture for the ambiguity judgment process.
**Decision:** Embedder ranks, judge decides.
1. Pre-process by embedding all column names from each table and store in pgvector.
2. User asks a question/query.
3. Vector embed the query (or in our case, the noun phrase).
4. Perform cosine similarity between each vectorized column name and the user's query noun phrase, tracking a top-k short list of highest similarity.
5. Put the query NP and the short list into a judge prompt which outputs `AMBIGUOUS`, `CLEAR`, or `REFUSE`, using the first-token logprob margin as a confidence gate: a low-margin `CLEAR` is treated as `AMBIGUOUS`.
6. Based on the output of the judge model: `AMBIGUOUS` asks a clarifying question, `REFUSE` says nothing matches (or offers the closest thing), `CLEAR` passes the query plus the matched columns into the SQL generation prompt.
**Why:** Ranking is reliable even when scoring isn't, so the right column lands in the top-k. The judge prompt stays small even as the schema grows. The margin gate turns low confidence into a clarifying question instead of a guess.
**Tradeoffs:** Two model calls before SQL generation. If the true column misses the top-k, the judge never sees it, so k errs generous.

## 📝 Constituency parse replaces the spaCy noun chunker for user query in RAG agent
**Context:** The SpaCy noun chunker missed any phrase without a noun head. e.g. "fiscal 2024" dropped. So it wasn't able to capture other POS phrases which could contain pertinent query information potentially matching columns. And simply patching failure classes one at a time was plugging a leaky ship.
**Decision:** Do a constituency parse using benepar and keep every span whose label is in {NP, PP, WHNP, ADVP}, emit (text, label) pairs, dedupe exact duplicates only.
**Why:** In a constituency tree the phrase is the node, so selection is just a label check. In terms of why keeping for SQL query: PP can carry filters and group-bys, and the preposition itself would likely be the linker (in/for = time, by/per = grouping). WHNP can carry SELECTs. NPs carry the query content like measures and entities ("the sales figure", "FreshDent Kids Toothbrush", "fiscal 2024"). Most SELECT targets and filter values arrive as NPs, so this is the ground label all the other constituents supplement. ADVPs don't do much here but carry grain information like "monthly", "quarterly", which are GROUP BYs.
**Tradeoffs:** An additional model, benepar, and so slower parses.

## 📝 Joint judge call with letter verdicts, margin-measured ambiguity for RAG agent
**Context:** Per-pair judging costs one generation per chunk and can't see overlap structure.
**Decision:** One prompt carries the question, numbered chunks, and each chunk's own candidates lettered A-C. Output is one line per chunk, `<n> -> <letter>`, or X for no fit, so every verdict is a single uppercase token. AMBIGUOUS is no longer a model label; it's measured per line as the logprob margin at the verdict token between the chosen letter and the best other valid option, with a low margin recorded as AMBIGUOUS plus the runner-up. Temperature 0, no grammar constraint (constrained decoding might distort the logprobs).
**Why:** N calls collapse to one. Single-token verdicts provide a simple one-token-one-decision, as opposed to multi-token column names. A hallucinated column becomes a parse failure instead of a lie. Measured ambiguity margin hands over the ambiguous pair, which becomes the content of the clarification question.

## 📝 Name-only column text for the joint prototype
**Context:** name+desc was marginally the best-performing column text in the judge evals, but I haven't written descriptions for this schema yet.
**Decision:** The prototype runs on raw column names, and descriptions to come later.
**Why:** Nothing relies on the inclusion of a description, so including it as a later addition changes nothing in the logic or flow, but is likely to improve performance based on initial tests.