from langchain_text_splitters import RecursiveCharacterTextSplitter
import config
import uuid

text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
)

def chunk_text(results:list) -> list:
    text_chunks=[]
    
    for res in results:
        raw_chunks = text_splitter.split_text(res['text'])

        for idx,txt in enumerate(raw_chunks):
            text_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "text": txt,
                "metadata": {
                    "source": res["source_path"],
                    "doc_id": str(res["id"]),
                    "chunk_index": idx
                }
            })
    return text_chunks