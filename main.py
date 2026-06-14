from fastapi import FastAPI, File, UploadFile
import uvicorn
from ingest_docs.ingest_manager import ingest
from rag_pipeline.query_preprocess.preprocess import preprocess_query
import io

app = FastAPI()

@app.post('/ingest-doc')
def ingest(files:list[UploadFile] = File(...)):
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
        ingest(file_info)
        return "Ingestion successfully completed!"

    except Exception as e:
        print(f'Error :{e}')
        return "Failed to ingest documents!"

@app.post('/query')
def query(query:str):
    # query preprocessing
    preprocess_query(query)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )