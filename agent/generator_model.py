import os
from openai import OpenAI
from prompt_sql_generation import exemplars

'''
Inference script for MODEL 2: main inference/actor model
'''
url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
model = os.getenv("LLM_MODEL", "llama3.1:8b")
api_key = os.getenv("LLM_API_KEY", "ollama")    ## ollama api key for local use

def load_client(url=url, api_key=api_key):
    return OpenAI(base_url=url, api_key=api_key)


def get_response(client, question, pairs, model=model, previous_sql=None, problems=()):
    matches = "\n".join(f'- "{segment}" -> {column}' for column, segment in pairs)
    messages = [
        {"role": "system", "content": exemplars},
        {"role": "user", "content": f"{question}\n\nColumns matched to parts of the question:\n{matches}"},
    ]
    ## retry: show the model its own sql and exactly what's wrong with it
    if problems:
        messages.append({"role": "assistant", "content": previous_sql})
        messages.append({"role": "user", "content": "Fix these and answer with only the corrected SQL:\n" + "\n".join(f"- {p}" for p in problems)})
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content