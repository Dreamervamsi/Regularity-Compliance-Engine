from ingest_docs.embedding import model
from fastembed import TextCrossEncoder
import config

class CrossEncoder:
    def __init__(self,api_key=None,model=config.RERANKER_MODEL):
        self.reranker = TextCrossEncoder(model_name=model)
        self.headers = {}
        if api_key:
            end_point="https://huggingface.co/{model}"



