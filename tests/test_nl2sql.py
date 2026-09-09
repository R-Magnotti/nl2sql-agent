'''
smoke test for the generation call: does the configured endpoint answer at all?

not an eval -- it asserts nothing about SQL quality, only that the client, the
model tag and the server line up. anything about which model answers *better*
belongs in evals/.

    pytest                         ## skips when the endpoint or model is missing
    pytest tests -m integration    ## the same, run deliberately
'''
import os

import pytest

from agent.nl2sql import get_response, load_client

URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
API_KEY = os.getenv("LLM_API_KEY", "ollama")


@pytest.fixture(scope="module")
def client():
    '''
    a live client serving MODEL, or a skip.

    the endpoint is a local ollama by default, so "nothing listening" and "that
    model was never pulled" both mean "not set up on this machine" rather than
    "broken" -- failing over either would make `pytest` red everywhere the agent
    simply is not installed. a served model that then errors is a real failure.
    '''
    c = load_client(url=URL, api_key=API_KEY)
    try:
        served = [m.id for m in c.models.list().data]
    except Exception as e:
        pytest.skip(f"no LLM endpoint at {URL} ({type(e).__name__}); "
                    f"start one with `ollama serve`")
    if MODEL not in served:
        pytest.skip(f"{URL} serves {served or 'nothing'}, not {MODEL}; "
                    f"`ollama pull {MODEL}` or set LLM_MODEL")
    return c


@pytest.mark.integration
def test_endpoint_answers(client):
    answer = get_response(client=client, model=MODEL,
                          question="what color is the sky in 1 word?")
    assert answer and answer.strip(), f"{MODEL} at {URL} returned nothing"
