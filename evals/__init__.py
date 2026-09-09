'''
model-quality evals: slow, model-dependent, and reported rather than gated.

kept apart from tests/ because the two answer different questions. tests/ asks
"is the code still correct", runs in seconds, and belongs in CI. this asks "which
model should the agent use", needs ~11GB of embedder weights and a live ollama,
and produces a table someone reads.
'''
