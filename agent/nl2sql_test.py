from nl2sql import load_client, get_response
import os

url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
model = os.getenv("LLM_MODEL", "llama3.1:8b")
api_key = os.getenv("LLM_API_KEY", "ollama")

client = load_client(url=url, api_key=api_key)
prompt = "what color is the sky in 1 word?"
res = get_response(client=client, model= model, question=prompt)
print(res)