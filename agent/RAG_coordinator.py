## this script should be called by nl2sql driver, and act as the full RAG pipeline

from Prompt import t
from nl2sql import load_client, get_response
from utils import clean_SQL_query_driver
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
prompt = t

'''
step 2: query knowledge base
step 3: return relevant info / exemplars
'''

## skipping knowledge base query for now

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
print(f'Cleaned SQL query: {sql_query}')

## execute sql on bigquery
query_res = bq_client.query(sql_query)

## display resulting table
for row in query_res.result():
    print(row)