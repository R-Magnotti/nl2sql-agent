'''
act/NLG = SQL generation and execution or generating the specific clarifying question
'''

from generator_model import load_client, model    ## same model as sql gen (llama3.1:8b), so ollama never loads a second one
from prompt_clarifying_question import t as clarify_prompt
from prompt_final_answer import t as answer_prompt

nlg_client = load_client()

## in: user question (str), ambiguous_segments from deliberate: list of tuples (question_segment, topk)
## out: one clarifying question (str) covering every ambiguous segment
def NLG_clarifying_question(question, ambiguous_segments):
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
    final_prompt = clarify_prompt.format(question=question, unclear_phrases=unclear_phrases)
    
    print(f"NLG prompt:\n{final_prompt}")

    response = nlg_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": final_prompt},
        ],
        temperature=0,
    )
    return response.choices[0].message.content


## in: user question (str), the sql that ran (str), result rows from bigquery
## out: plain english answer for the user (str)
## {'calendar_quarter': 4} --> "calendar quarter 4 (October to December) as the quarter with the highest sales."
def NLG_final_answer(question, sql, rows):
    ## a bigquery Row prints as Row((4,), {'calendar_quarter': 0}), where 0 is a position not a value,
    ## so hand the model plain dicts like {'calendar_quarter': 4}
    rows = [dict(row) for row in rows]
    final_prompt = answer_prompt.format(question=question, sql=sql, rows=rows)

    print(f"NLG answer prompt:\n{final_prompt}")

    response = nlg_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": final_prompt},
        ],
        temperature=0,
    )
    return response.choices[0].message.content


