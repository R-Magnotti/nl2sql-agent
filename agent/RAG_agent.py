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

from prompt_user_question import t
from actor_model import load_client, get_response
from utils import clean_SQL_query_driver, vector_search
from google.cloud import bigquery

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
ollama_client = load_client()
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
gt_labels = ["NP", "PP", "WHNP", "AdvNP"]
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
from critic_model import load_client as load_critic_client, get_response as ask_critic

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

raise SystemExit  
## TODO: ambiguity catch + clarification loop
## TODO: send matched (query chunk, col name) pairs to final actor model to generate final SQL qeuery, query against BigQuery, return answer (to user) 

res = ask_critic(client=critic_client, question=prompt, chunks=prompt_block)
print(res)


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