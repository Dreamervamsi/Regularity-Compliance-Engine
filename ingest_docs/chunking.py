from langchain_text_splitters import RecursiveCharacterTextSplitter
import config
import uuid

text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
)

def chunk_text(parsed_sections:list) -> list:
    text_chunks=[]
    
    for section in parsed_sections:
        
        section_title = section['section_title']
        section_content = section['text']
        source_path = section['source_path']

        if len(section_content) <= config.CHUNK_SIZE:
            text_chunks.append({
                "chunk_id":str(uuid.uuid4()),
                "text":section_content,
                "metadata":{
                    "source":source_path,
                    "doc_id":section['id'],
                    "section_title":section_title,
                    "chunk_index":0
                }
            })
        else:
            raw_chunks = text_splitter.split_text(section_content)

            for idx,txt in enumerate(raw_chunks):
                text_chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "text": txt,
                    "metadata": {
                        "source": source_path,
                        "doc_id": section['id'],
                        "section_title":section_title,
                        "chunk_index": idx
                    }
                })
    return text_chunks