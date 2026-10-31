'''
sense/NLU = "understand" / classify the question by assessing the ambiguity
'''

import spacy
import benepar

from agent_utils import embed_model, vector_search

## only keep labeled chunks which could contain useful information about SQL query
## labels from treebank
gt_labels = {"NP",      ## noun phrase
             "PP",      ## prepositional phrase
             "WHNP",    ## wh-noun phrase "what", "which", etc
             "ADVP"}    ## adverb phrase
noun_tags = {"NN",      ## singular noun
             "NNS",     ## plural noun
             "NNP",     ## singular proper noun "Amazon"
             "NNPS"}    ## plural proper noun "Americans"

## models load once at import, not once per NLU() call
## chunk user query into CONSTITUENTS (not NPs, see DECISIONS.md for more detail)
nlp = spacy.load("en_core_web_sm")  ## can change to en_core_web_trf if value accuracy > speed
nlp.add_pipe("benepar", config={"model": "benepar_en3"})    ## spacy doesn't do constituency parse by default


## in: user question (str), k = number of candidate columns per question segment
## out: dict, key: question segment (spacy span), value: its topk column names
def NLU(question, k):
    segment_topk_dict = {}

    doc = nlp(question)
    sent = list(doc.sents)[0]

    ## extract each question segment, embed it, then vector search
    for question_segment in sent._.constituents:   ## each question_segment is a spacy span
        
        ## if segment is a phrase
        if question_segment._.labels:
            if not gt_labels & set(question_segment._.labels):
                continue
        ## if segment is a bare word "the"
        elif question_segment[0].tag_ not in noun_tags:   # bare word, check its POS tag
            continue
        
        print(f"Constituent: {question_segment.text}, Label: {question_segment._.labels}")
        embedded_segment = embed_model.encode(question_segment.text)
        topk = vector_search(embedded_segment, k)
        segment_topk_dict[question_segment] = topk

    return segment_topk_dict