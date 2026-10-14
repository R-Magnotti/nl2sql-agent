''' 
this script should be called by nl2sql driver, and act as the full RAG pipeline 

purpose of this script is to:
- chunk user query + vector embed user input query
- vector search knowledge base for matching terms
- inject matches into judge prompt, and run judge LLM
- pass judge-approved output into final inference LLM

OVERALL INPUT: user query
OVERALL OUTPUT: llm response to user query
'''

import spacy
import benepar
import math

from prompt_user_question import t
import sql_gen_model
from utils import clean_SQL_query_driver, vector_search, get_critic_picks, is_valid_sql
from google.cloud import bigquery
from critic_model import load_client as load_critic_client, get_response as ask_critic

'''
Components:
- knowledge base
- retriever + ranker
- coordinator
- generator
'''

'''
step 1: get the prompt 
'''
ollama_client = sql_gen_model.load_client()
bq_client = bigquery.Client()

## read from prompt.py file
prompt = t.strip()   ## benepar's retokenizer asserts on whitespace-only tokens
print(f'Q: {t}')

'''
step 2: query knowledge base
'''
## embedding model
from sentence_transformers import SentenceTransformer
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

## only keep labeled chunks which could contain useful information about SQL query
gt_labels = ["NP", "PP", "WHNP", "ADVP"] ## labels from treebank
chunk_dict = {} ## key: chunk str, value: chunk vector embedding

## topk, set to taste
k = 3

## chunk user query into CONSTITUENTS (not NPs, see DECISIONS.md for more detail)
nlp = spacy.load("en_core_web_sm")  ## can change to en_core_web_trf if value accuracy > speed
nlp.add_pipe("benepar", config={"model": "benepar_en3"})    ## spacy doesn't do constituency parse by default
doc = nlp(prompt)

sent = list(doc.sents)[0]   

## extract each chunk, embed it, then vector search
for c in sent._.constituents:   ## each c is a span
    print(f"Constituent: {c.text}, Label: {c._.labels}")
    embedded_chunk = embed_model.encode(c.text)
    topk = vector_search(embedded_chunk, k)
    chunk_dict[c] = topk
    
## pass constituent chunks and topk matched for each to judge prompt
critic_client = load_critic_client()
letters = "ABC"   ## k candidates per chunk, num letters = k

## step 4 can read a reply like "2 -> C" straight back to chunks[1]
chunks = list(chunk_dict.items())

## build the numbered prompt block the critic prompt asks for:
##   1. "phrase"
##      A. option 1
##      B. option 2
##      ...
lines = []
number = 1

for chunk, topk in chunks:
    lines.append(f'{number}. "{chunk.text}"')

    for i in range(len(topk)):
        lines.append(f"   {letters[i]}. {topk[i]}")

    number += 1

prompt_block = "\n".join(lines)

print(f"\n\nChunks block:\n{prompt_block}")

res, logprobs, messages = ask_critic(client=critic_client, question=prompt, chunks=prompt_block)
print(res)

served_prompt = "\n".join(m["content"] for m in messages)  ## system + user text, in order

## loop through critic model output for token log probs
gen_so_far = ""
for i, logprob_data in enumerate(logprobs):
    input_to_pass_i = served_prompt + gen_so_far   ## <-- input sequence of fwd pass i
    print(f"\n--- pass {i} ---")
    print(f"Input to forward pass {i} \n {input_to_pass_i[-10:]}\n")
    for topklogprob in logprob_data.top_logprobs:
        p = math.exp(topklogprob.logprob)
        print(f"Top k token: {topklogprob.token!r} | Prob: {p:.4f}")
    gen_so_far += logprob_data.token
    
##TODO: next would be ambiguity detection using logprobs, but skipping for right now

## use regex to extract critic output top pick for each user input segment
critic_picks = get_critic_picks(res)

print("\n")
pairs = []
for number, letter in critic_picks:
    chunk, topk = chunks[int(number) - 1]
    column = topk[letters.index(letter)]    ## "A" -> 0, "B" -> 1, "C" -> 2
    pairs.append((column, chunk.text))
    print(pairs[-1])

## NOTE: SKIPS ambiguity detection and clarification loop for now...focusing on sql gen pipeline first

## send matched (query chunk, col name) pairs list to sql gen model to generate final SQL qeuery, query against BigQuery, return answer (to user) 
sql = sql_gen_model.get_response(client=ollama_client, question=prompt, pairs=pairs)
print("\n", sql)

## use sqlglot to make sure output is valid
valid = is_valid_sql(sql)

## TODO: handle if not case

## if sql is valid, run against bigquery
if valid:
    query_res = bq_client.query(sql)
    for row in query_res.result():
        print(row)
    

raise SystemExit  


'''
step 4: inject knowledge into original prompt
'''

'''
step 5: pass updated prompt to main LLM, and receive output
'''
## get response
res = get_response(client=ollama_client, question=prompt)

## clean response
sql_query = clean_SQL_query_driver(res)
print(f'\nCleaned SQL query: \n{sql_query}')

## execute sql on bigquery
query_res = bq_client.query(sql_query)

## display resulting table
for row in query_res.result():
    print(row)