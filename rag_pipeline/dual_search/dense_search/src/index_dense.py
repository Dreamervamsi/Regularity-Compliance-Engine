import chromadb
import config
import os

def get_client():
    client = chromadb.PersistentClient(path=os.path.join(config.INDEX_DIR,"chroma"))
    return client 

def get_collection(full_reingest:bool=False,collection_name:str=config.CHROMADB_COLLECTION):
    client = get_client()
    if full_reingest:
        try:
            client.delete_collection(name=collection_name)
            print(f"Cleared existing collection: {config.INDEX_DIR}")
        except ValueError:
            pass

    collection = client.get_or_create_collection(
        name=config.CHROMADB_COLLECTION,
        embedding_function=None,
        metadata={"hnsw:space": "cosine"}
    )

    return collection

def vector_store(chunks:list,embeddings:list,full_reingest:bool=False):
    
    documents=[]
    ids=[]
    metadatas=[]
    
    collection = get_collection(full_reingest)

    for chunk in chunks:
        
        documents.append(chunk['text'])
        ids.append(chunk['chunk_id'])
        metadatas.append(chunk['metadata'])
    
    collection.upsert(
        documents=documents,
        ids=ids,
        metadatas=metadatas,
        embeddings=embeddings
    )

    return collection


def dense_search(query_embedding, top_k,where_clause:dict=None) -> list:

    collection = get_collection(False)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_clause
    )

    formatted_results = []

    for i in range(len(results['ids'][0])):
        formatted_results.append({
            'chunk_id':results['ids'][0][i],
            'text':results['documents'][0][i],
            'metadata':results['metadatas'][0][i],
            'distance':float(results['distances'][0][i])
        })
    
    return formatted_results