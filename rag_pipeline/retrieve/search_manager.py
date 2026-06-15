from rag_pipeline.dual_search.sparse_search.src.sparse_index import Tokenize
import config
from rag_pipeline.dual_search.dense_search.src.index_dense import dense_search
from ingest_docs.embedding import model
from rag_pipeline.retrieve.rrf_ranking import reciprocal_rank_fusion
from rag_pipeline.rag.llm import generate_rag
from rag_pipeline.retrieve.metadata_filter import construct_metadata_filter,filter_chunks

tokenizer = Tokenize()
tokenizer.load_chunks(file_path=config.CHUNK_FILE)

def search(user_query:str,top_k:int=config.TOP_K,regulation_name:str=None,section_name:str=None):
    try:
        query = user_query
        
        query_embedding = next(model.embed([query]))

        # construct metadata filter
        where_clause = construct_metadata_filter(
            regulation=regulation_name,
            section=section_name
        )

        if where_clause:
            chunks = filter_chunks(chunks,regulation=regulation_name,section=section_name)
        # sparse search
        # higher top_k for sparse search to get more relevant results
        sparse_results = tokenizer.sparse_search(query,top_k*4)
        
        # dense search
        # higher top_k for dense search to get more relevant results
        dense_results = dense_search(query_embedding,top_k*4)
        
        res = reciprocal_rank_fusion(sparse_results,dense_results,k=60,top_k=top_k)

        rag_result = generate_rag(query,res)

        return rag_result

    except FileNotFoundError as e:
        print(f"File not found error:{e}") 
    except Exception as e:
        # Left open as requested, but added a basic pass/print to avoid compilation crash
        print(f"An error occurred: {e}")