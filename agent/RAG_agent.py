''' 
this script should be called by nl2sql driver, and act as the full RAG pipeline 

purpose of this script is to (steps):
1. chunk user query + vector embed user input query
2. vector search knowledge base for matching terms
3. inject matches into judge prompt, and run judge LLM
4. detect in-out pair ambiguities 
5. ask user for additional targeted disambiguating information
    Loop steps 2-4 until no ambiguities or no matches
6. pass judge-approved output into downstream inference LLM

OVERALL INPUT: user query
OVERALL OUTPUT: llm response to user query
'''

from prompt_user_question import t
import generator_model
from agent_utils import clean_SQL_query_driver, get_critic_picks, is_valid_sql, TOP_K
from NLU import NLU
from deliberate import deliberate
from NLG import NLG
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
ollama_client = generator_model.load_client()
bq_client = bigquery.Client()

## read from prompt.py file
prompt = t.strip()   ## benepar's retokenizer asserts on whitespace-only tokens
print(f'Q: {t}')


'''
step 2: query knowledge base
'''
## key: question segment (spacy span), value: its topk column names
segment_topk_dict = NLU(prompt, TOP_K)
   
    
'''
steps 3-4: critic picks a column for each question segment, then sort picks into ambiguous / clear / clear no match
'''
ambiguous_segments, clear_matches, no_match_segments = deliberate(prompt, segment_topk_dict)


'''
step 5: ask user for additional targeted disambiguating information
'''
if len(ambiguous_segments) != 0: ## have some ambiguities to resolve
    ## only want to run this ONCE so as not to inundate user with questions

    ## effectively loop steps 2-4 until no ambiguities or no matches
    print(f'\n-----------\nAmbiguities detected, starting clarification loop ...')
    
    ## NLG writes one clarifying question that covers all ambiguities
    clarifying_question = NLG(prompt, ambiguous_segments)
    print(clarifying_question)

    ## let the user answer the clarifying question
    user_answer = input("> ").strip()   ## benepar asserts on whitespace-only input

    ## rerun steps 2-4 once, with the user's answer added to the question
    if user_answer:
        prompt = f"{prompt} {user_answer}"
        segment_topk_dict.update(NLU(user_answer, TOP_K))   ## step 2 only needs the new words
        ambiguous_segments, clear_matches, no_match_segments = deliberate(prompt, segment_topk_dict)
    
## if no ambiguity or already did 1 round of clarification, pipe to sql generator
## send matched (query chunk, col name) pairs list to sql gen model to generate final SQL qeuery, query against BigQuery, return answer (to user) 
sql = generator_model.get_response(client=ollama_client, question=prompt, pairs=clear_matches)
print("\n", sql)

## use sqlglot to make sure output is valid
valid = is_valid_sql(sql)

## TODO: handle if not valid SQL case

## if sql is valid, run against bigquery
if valid:
    query_res = bq_client.query(sql)
    for row in query_res.result():
        print(row)