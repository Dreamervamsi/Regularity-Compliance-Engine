from rag_pipeline.dual_search.sparse_search.src.sparse_index import Tokenize
import config
from rag_pipeline.dual_search.dense_search.src.index_dense import dense_search
from ingest_docs.embedding import model
from rag_pipeline.retrieve.rrf_ranking import reciprocal_rank_fusion
from rag_pipeline.rag.llm import generate_rag
from rag_pipeline.retrieve.metadata_filter import construct_metadata_filter,filter_chunks
from rag_pipeline.cache.semantic_cache import search_exact_query,store_semantic_query,get_redis
from redis.asyncio import Redis
from fastapi import Depends

tokenizer = Tokenize()
tokenizer.load_chunks(file_path=config.CHUNK_FILE)

async def search(user_query:str,top_k:int,regulation_names:list,section_name:str,redis:Redis):
    try:
        query = user_query
        
        query_embedding = next(model.embed([query]))
        
        # exact cache search
        exact_match = await search_exact_query(query,redis)
        if exact_match:
            return exact_match
        #semantic cache search
        semantic_match = await search_semantic_query(query_embedding,redis)
        if semantic_match:
            return semantic_match
        
        # construct metadata filter
        where_clause = construct_metadata_filter(
            regulations=regulation_names,
            section=section_name
        )
        orgi_chunks = tokenizer.org_chunks
        if where_clause:
            org_chunks = orgi_chunks
            chunks = filter_chunks(org_chunks,regulation=regulation_names,section=section_name)
        
        # sparse search
        # higher top_k for sparse search to get more relevant results
        
        sparse_results = tokenizer.sparse_search(chunks,query,top_k*4)
        
        # dense search
        # higher top_k for dense search to get more relevant results
        dense_results = dense_search(query_embedding,top_k*4,where_clause=where_clause)
        
        res = reciprocal_rank_fusion(sparse_results,dense_results,k=60,top_k=top_k)

        rag_result = generate_rag(query,res)
        
        # storing the rag response
        await store_semantic_query(query,query_embedding,rag_result,redis)

        return rag_result

    except FileNotFoundError as e:
        print(f"File not found error:{e}") 
    except Exception as e:
        # Left open as requested, but added a basic pass/print to avoid compilation crash
        print(f"An error occurred: {e}")