from rank_bm25 import BM25Okapi
import os,json

class Tokenize:
    def __init__(self):
        self.org_chunks = [] 
        self.tokenize_corpus = None

    def init_chunks(self,chunks:list):
        if not chunks:
            raise ValueError('Text chunks not provided')

        self.org_chunks = chunks
        self.build_index()
        

    def build_index(self):
        if not self.org_chunks:
            self.corpus = []
            self.tokenize_corpus = None
            return

        self.corpus=[self.org_chunks[i]['text'].lower().split() for i in range(len(self.org_chunks))]
    
        self.tokenize_corpus = BM25Okapi(self.corpus)

    def sparse_search(self,chunks:list,query:str,top_k:int=3):
        
        tokenized_query = query.lower().split()

        temp_corpus = [chunk['text'].lower().split() for chunk in chunks]
        temp_bm25 = BM25Okapi(temp_corpus)
        
        scores = temp_bm25.get_scores(tokenized_query)

        scored_chunks = []

        for idx, chunk in enumerate(chunks):
            scored_chunks.append({
                "chunk_id": chunk.get("chunk_id"),
                "text": chunk.get("text"),
                "metadata": chunk.get("metadata"),
                "sparse_score": float(scores[idx])
            })

        scored_chunks.sort(key=lambda x:x['sparse_score'],reverse=True)
        
        return scored_chunks[:top_k]
    
    def save_chunks(self,chunks:list,file_path:str,full_reingest:bool):
           
        if full_reingest or not os.path.exists(file_path): # if chunk.json not exists it will just create empty list
            existing_chunks=[]
        else:  # if chunk.json exists it will read contents of chunk.json and place it into existing_chunks list
            try:
                with open(file_path,"r",encoding="utf-8") as f:
                    existing_chunks=json.load(f) # json.load is a method used to read and parse incoming file
            except (json.JSONDecodeError, FileNotFoundError):
                existing_chunks=[]

        existing_ids={chunk.get('chunk_id') for chunk in existing_chunks if chunk.get('chunk_id')}

        for chunk in chunks:
            if chunk['chunk_id'] and chunk['chunk_id'] not in existing_ids:
                existing_chunks.append(chunk)

        with open(file_path,"w",encoding="utf-8") as f:
            json.dump(existing_chunks,f,indent=4)  # it takes input as python object[dist,dict,etc..] and write the contents into .json file

        self.org_chunks = existing_chunks
        self.build_index()
    
    def load_chunks(self,file_path:str):
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not exists")

        with open(file_path,"r",encoding="utf-8") as f:
            self.org_chunks = json.load(f)
        
        self.build_index()