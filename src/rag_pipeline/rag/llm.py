from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import HumanMessage
from src.schemas import ComplianceResult, Source
import os
from logging import getLogger
import config
from dotenv import load_dotenv
import json

logger = getLogger(__name__)

load_dotenv()

hf_token = os.getenv('HF_TOKEN')

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    task="text-generation",
    max_new_tokens=512,
    huggingfacehub_api_token=hf_token
)

chat_model = ChatHuggingFace(llm=llm)
strucured_model = chat_model.with_structured_output(ComplianceResult)

def _retry_response(messages,max_retries:int = config.RESPONSE_MAX_RETRIES):
    current_retry = 0
    while current_retry <= max_retries:
        try:
            response = strucured_model.invoke(messages)

            if response.confidence_score < 0.0 or response.confidence_score > 1.0:
                logger.warning(f"Confidence score {response.confidence_score} is out of range. Retrying.")
                current_retry += 1
                continue
            
            return response

        except Exception as e:
            logger.error(f"Error in retry response: {e}")
            current_retry += 1
    
    return None

def _generate_rag_results(query:str,top_results:list):
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
        Your response will automatically populate a structured data object. Follow these rules to fill it:
        
        1. 'answer': Write your final answer here using information ONLY found in the context.
        2. 'sources': Extract the document names, section titles and page numbers used to build your answer.
        3. 'confidence_score': Assign a float value between 0.0 and 1.0 representing your certainty.
        4. 'refused': Set this to TRUE if the context does not contain the answer. Otherwise, set it to FALSE."

        CONTEXT_BLOCK:
            [DOCUMENT CONTEXT]
            {formatted_context}

        [USER QUESTION]
        {query}

        """
    messages = [
        HumanMessage(content=rag_prompt)
    ]

    response = strucured_model.invoke(messages)
    
    if response.refused == True:
        retry_response = _retry_response(messages)
        if retry_response:
            response = retry_response
    
    citations = []
    for idx, result in enumerate(top_results, start=1):
        source_file = result['metadata']['source']
        chunk_index = result['metadata']['chunk_index']
        score = result.get('rrf_score', 0.0)
        
        citations.append(f"[{idx}] Source: {source_file} (Chunk {chunk_index}) | RRF Score: {score:.4f}")

    if response:
        if response.confidence_score < 40:
            
            response.refused = True
        else:
            return response.answer,citations
    
    return "Unable to process the request!"

def generate_rag(query:str,top_k_results:list):
    
    return _generate_rag_results(query,top_k_results)