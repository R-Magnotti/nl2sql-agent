'''
act/NLG = SQL generation and execution or generating the specific clarifying question
'''

from generator_model import load_client, model    ## same model as sql gen (llama3.1:8b), so ollama never loads a second one
from prompt_clarifying_question import t as clarify_prompt

nlg_client = load_client()

## in: user question (str), ambiguous_segments from deliberate: list of tuples (question_segment, topk)
## out: one clarifying question (str) covering every ambiguous segment
def NLG(question, ambiguous_segments):
    ## build the numbered block the clarifying prompt asks for:
    ##   1. "phrase"
    ##      - option 1
    ##      - option 2
    ##      ...
    lines = []
    number = 1

    for question_segment, topk in ambiguous_segments:
        lines.append(f'{number}. "{question_segment.text}"')

        for column in topk:
            lines.append(f"   - {column}")
        number += 1

    unclear_phrases = "\n".join(lines)

    response = nlg_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": clarify_prompt.format(question=question, unclear_phrases=unclear_phrases)},
        ],
        temperature=0,
    )
    return response.choices[0].message.content


