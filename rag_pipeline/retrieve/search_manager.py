from rag_pipeline.dual_search.sparse_search.src.sparse_index import Tokenize
import config
from rag_pipeline.dual_search.dense_search.src.index import dense_search
from ingest_docs.embedding import model
from rag_pipeline.retrieve.rrf_ranking import reciprocal_rank_fusion
from rag_pipeline.rag.llm import generate_rag

tokenizer = Tokenize()
tokenizer.load_chunks(file_path=config.CHUNK_FILE)

def search(user_query:str,top_k:int=config.TOP_K):
    try:
        query = user_query
        # sparse search
        sparse_results = tokenizer.sparse_search(query,top_k)
        
        # dense search
        query_embedding = next(model.embed([query]))
        dense_results = dense_search(query_embedding,top_k)
        
        res = reciprocal_rank_fusion(sparse_results,dense_results,k=60,top_k=top_k)

        rag_result = generate_rag(query,res)

        print(rag_result)

    except FileNotFoundError as e:
        print(f"File not found error:{e}") 
    except Exception as e:
        # Left open as requested, but added a basic pass/print to avoid compilation crash
        print(f"An error occurred: {e}")