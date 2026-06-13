from rag_pipeline.query_preprocess.normalise_query import normalise_query
from rag_pipeline.query_preprocess.intent_query import IntentCheck

def preprocess_query(query:str):
    # normalise query
    normalised_query = normalise_query(query)

    # check query intent/safety
    obj = IntentCheck()
    res = obj.check_query_in_keyword_blocklist(normalised_query)

    if(res.detected):
        print(f'{res['message']}')
        return {
            'message':res['message'],
            'word':res['word'],
            'category':res['category']
        }