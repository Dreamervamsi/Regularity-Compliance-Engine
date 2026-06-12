from functools import lru_cache
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
import json

load_dotenv()

hf_token = os.getenv('HF_TOKEN')

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    task="text-generation",
    max_new_tokens=512,
    huggingfacehub_api_token=hf_token
)

chat_model = ChatHuggingFace(llm=llm)

@lru_cache(maxsize=128) # lazy initialising or caching response if sae query passed
def _generate_rag_results(query:str,top_results:str):
    context_block=[]
    for idx,result in enumerate(top_results,start=1):
        block = (
            f"--- Document Source [{idx}] ---\n"
            f"File: {result['metadata']['source']}\n"
            f"Retrieval Confidence Score: {result.get('rrf_score', 'N/A')}\n"
            f"Content: {result['text']}\n"
        )
        context_block.append(block)

    formatted_context = "\n".join(context_block)

    rag_prompt = f"""
        You are a helpful assistant answering questions based strictly on the provided document context.
        If the answer cannot be found in the context, politely say that you do not know. Do not make things up.
        
        [DOCUMENT CONTEXT]
        {formatted_context}

        [USER QUESTION]
        {query}

        [FINAL ANSWER]
        """
    messages = [
        HumanMessage(content=rag_prompt)
    ]

    response = chat_model.invoke(messages)
    citations = []
    for idx, result in enumerate(top_results, start=1):
        source_file = result['metadata']['source']
        chunk_idx = result['metadata']['chunk_idx']
        score = result.get('rrf_score', 0.0)
        
        citations.append(f"[{idx}] Source: {source_file} (Chunk {chunk_idx}) | RRF Score: {score:.4f}")

    return response.content,citations

def generate_rag(query:str,top_k_results:list):
    
    serialise = json.dump(top_k_results,sort_keys=True)

    return _generate_rag_results(query,serialise)