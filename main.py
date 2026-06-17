from fastapi import FastAPI, File, UploadFile, Depends, status, HTTPException
import uvicorn
from ingest_docs.ingest_manager import ingest
from rag_pipeline.query_preprocess.preprocess import preprocess_query
import io
from rag_pipeline.retrieve.search_manager import search
from redis.asyncio import Redis
from rag_pipeline.cache.semantic_cache import get_redis

app = FastAPI()

@app.post('/ingest-doc',status_code=status.HTTP_201_CREATED)
async def ingest_doc(files:list[UploadFile] = File(...)):
    try :
        file_info=[]
        for file_num,file in enumerate(files,start=1):
            binary_content = file.file.read()
            io_bytes = io.BytesIO(binary_content)

            file_info.append({
                "stream":io_bytes,
                "file_name":file.filename,
                "file_no":file_num
            })

        # ingesting document 
        await ingest(file_info)
        return "Ingestion successfully completed!"

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to ingest documents!:{e}"
        )

@app.post('/query',status_code=status.HTTP_200_OK)
def query(query:str,regulations:list=[],section:str=None,redis:Redis=Depends(get_redis)):
    if not regulations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide at least one regulation to search!"
        )
    
    # query preprocessing
    clean_query = preprocess_query(query)

    return search(clean_query,top_k=config.TOP_K,regulation_name=regulations,section_name=section,redis=redis)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )