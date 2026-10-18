'''
deliberate = the decide-or-ask policy, and if "ask" a communicative intent of what to ask
'''

import math

from agent_utils import judge_ambiguous
from critic_model import load_client as load_critic_client, get_response as ask_critic

critic_client = load_critic_client()
letters = "ABC"   ## k candidates per chunk, num letters = k


## in: user question (str), segment_topk_dict from NLU
## out: the 3 buckets: ambiguous_segments, clear_matches, no_match_segments
def deliberate(question, segment_topk_dict):

    ## step 3: pass vector search relevant matches to critic model
    ## step 4 can read a reply like "2 -> C" straight back to segment_topk_pairs[1]
    segment_topk_pairs = list(segment_topk_dict.items())    ## list of pairs: (question_segment, topk)

    ## build the numbered prompt block the critic prompt asks for:
    ##   1. "phrase"
    ##      A. option 1
    ##      B. option 2
    ##      ...
    lines = []
    number = 1

    for question_segment, topk in segment_topk_pairs:
        lines.append(f'{number}. "{question_segment.text}"')

        for i in range(len(topk)):
            lines.append(f"   {letters[i]}. {topk[i]}")
        number += 1

    prompt_block = "\n".join(lines)

    print(f"\n\nChunks block:\n{prompt_block}")

    ## step 4: detect in-out pair ambiguities
    res, logprobs, messages = ask_critic(client=critic_client, question=question, chunks=prompt_block)
    print(res)

    served_prompt = "\n".join(m["content"] for m in messages)  ## system + user text, in order

    ##  loop through critic model output for token log probs
    ##  logprobs is list of model output tokens. each token has a logprob_data:
    ##      .token:, .logprob (of token), .top_logprobs (topk likeliest tokens at that pass, with .token and .logprob)
    gen_so_far = ""
    ambiguous_segments = []   ## segments to rerun retrieval for, after the loop
    clear_matches = []        ## (column, question segment) pairs for the sql gen model
    no_match_segments = []    ## segments where the critic clearly said no column fits (X)
    for i, logprob_data in enumerate(logprobs):
        input_to_pass_i = served_prompt + gen_so_far   ## <-- input sequence of fwd pass i
        gen_so_far += logprob_data.token

        ## A/B/C/D/X correspond to column names or no match ('X')
        target_tokens = {"A": 0.0, "B": 0.0, "C": 0.0, "X": 0.0}

        ## if model top_i token is not desired letter --> skip
        if logprob_data.token.strip() not in target_tokens:
            continue

        print(f"\n--- pass {i} ---")
        print(f"Input to forward pass {i} \n {input_to_pass_i[-10:]}\n")

        for top_i in logprob_data.top_logprobs:
            p = math.exp(top_i.logprob)
            print(f"Top k token: {top_i.token!r} | Prob: {p:.4f}")
            token = top_i.token.strip()
            if token in target_tokens:
                target_tokens[token] += p ## to make sure 'B' and ' B' both count for 'B'
        print(target_tokens)

        ## which question segment this letter is for
        current_line = input_to_pass_i.split("\n")[-1]   ## e.g. "19 ->"
        number = int(current_line.split("->")[0])        ## 19
        if not 1 <= number <= len(segment_topk_pairs):   ## in case critic writes a line for a segment that doesn't exist
            continue
        question_segment, topk = segment_topk_pairs[number - 1]

        ## check for ambiguities, store the user input question segment if ambiguous --> else store the clear match
        letter = logprob_data.token.strip()
        if judge_ambiguous(target_tokens):
            ambiguous_segments.append((question_segment, topk))
        elif letter != "X":     ## X = no column fits, nothing to pass on
            column = topk[letters.index(letter)]
            clear_matches.append((column, question_segment.text))
        else:
            no_match_segments.append(question_segment.text)

    ## show all buckets
    print("\nAmbiguous:")
    for question_segment, topk in ambiguous_segments:
        print(f'  "{question_segment.text}" -> {topk}')

    print("\nClear matches:")
    for column, segment in clear_matches:
        print(f'  "{segment}" -> {column}')

    print("\nClear, no match (X):")
    for segment in no_match_segments:
        print(f'  "{segment}"')

    return ambiguous_segments, clear_matches, no_match_segments
