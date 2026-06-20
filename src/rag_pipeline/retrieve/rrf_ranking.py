import config

def reciprocal_rank_fusion(sparse_res:list,dense_res:list,k:int=60,top_k:int=config.TOP_K):
    rrf_scores = {}
    doc_data = {}

    for i,match in enumerate(sparse_res):
        doc_id = match.get('chunk_id')

        if doc_id not in rrf_scores:
            rrf_scores[doc_id] = 0.0
            doc_data[doc_id] = match
        
        # RRF calculation / formula
        rrf_scores[doc_id] += 1.0 / (k+i)
    for i,match in enumerate(dense_res):
        doc_id = match.get('chunk_id')

        if doc_id not in rrf_scores:
            rrf_scores[doc_id] = 0.0
            doc_data[doc_id] = match
            
        rrf_scores[doc_id] += 1.0 /(k+i)

    sorted_docs = sorted(rrf_scores.items(),key=lambda x:x[1], reverse=True)
    
    hybrid_results = []
    for doc_id, score in sorted_docs:
        final_match = doc_data[doc_id].copy()
        final_match['rrf_score'] = score
        hybrid_results.append(final_match)
    
    return hybrid_results[:top_k]