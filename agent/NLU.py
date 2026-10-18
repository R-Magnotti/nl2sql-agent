'''
sense/NLU = "understand" / classify the question by assessing the ambiguity
'''

import spacy
import benepar

from agent_utils import embed_model, vector_search

## only keep labeled chunks which could contain useful information about SQL query
gt_labels = ["NP", "PP", "WHNP", "ADVP"] ## labels from treebank

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
        print(f"Constituent: {question_segment.text}, Label: {question_segment._.labels}")
        embedded_segment = embed_model.encode(question_segment.text)
        topk = vector_search(embedded_segment, k)
        segment_topk_dict[question_segment] = topk

    return segment_topk_dict
