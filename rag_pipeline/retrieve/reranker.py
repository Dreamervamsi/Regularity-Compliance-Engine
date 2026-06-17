from ingest_docs.embedding import model
from fastembed import TextCrossEncoder
import config

class CrossEncoder:
    def __init__(self,api_key=None,model=config.RERANKER_MODEL):
        self.reranker = TextCrossEncoder(model_name=model)
        if api_key:
            self.end_point="https://huggingface.co/{model}"
            self.headers["Authorization"]=f"Bearer {api_key}"



