import os
from openai import OpenAI
from prompt_critic_model import t as critic_prompt

'''
Inference script for MODEL 1: llm judge/critic model
'''
url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
# model = os.getenv("LLM_MODEL", "qwen3:4b")
model = os.getenv("LLM_MODEL", "gemma3:1b") ## enabling a cheaper non-thinking model just for testing
api_key = os.getenv("LLM_API_KEY", "ollama") 

def load_client(url=url, api_key=api_key):
    return OpenAI(base_url=url, api_key=api_key)


## the whole critic prompt is: rules, a worked example and the live
## user query/question which all arrive together
def get_response(client, question, chunks, model=model):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": critic_prompt.format(question=question, chunks=chunks)},
        ],
        temperature=0,
        logprobs=True,
        top_logprobs=5,
    )
    return response.choices[0].message.content, response.choices[0].logprobs.content

def get_response(client, question, chunks, model=model):
    messages = [
        {"role": "user", "content": critic_prompt.format(question=question, chunks=chunks)},
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        logprobs=True,
        top_logprobs=5,
    )
    return response.choices[0].message.content, response.choices[0].logprobs.content, messages