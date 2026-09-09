import os
from openai import OpenAI
from agent.prompt_exemplars import exemplars

url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
model = os.getenv("LLM_MODEL", "llama3.1:8b")
api_key = os.getenv("LLM_API_KEY", "ollama")    ## ollama api key for local use

def load_client(url=url, api_key=api_key):
    return OpenAI(base_url=url, api_key=api_key)


def get_response(client, model=model, question="What color is the sky?"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": exemplars},
            {"role": "user", "content": question},
        ],
        temperature=0
    )
    return response.choices[0].message.content