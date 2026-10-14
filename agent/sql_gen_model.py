import os
from openai import OpenAI
from prompt_exemplars import exemplars

'''
Inference script for MODEL 2: main inference/actor model
'''
url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
model = os.getenv("LLM_MODEL", "llama3.1:8b")
api_key = os.getenv("LLM_API_KEY", "ollama")    ## ollama api key for local use

def load_client(url=url, api_key=api_key):
    return OpenAI(base_url=url, api_key=api_key)


def get_response(client, question, pairs, model=model):
    matches = "\n".join(f'- "{segment}" -> {column}' for column, segment in pairs)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": exemplars},
            {"role": "user", "content": f"{question}\n\nColumns matched to parts of the question:\n{matches}"},
        ],
        temperature=0
    )
    return response.choices[0].message.content