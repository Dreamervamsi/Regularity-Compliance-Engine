from fastapi import FastAPI, File, UploadFile
import uvicorn
from ingest_docs.ingest_manager import ingest
import io

app = FastAPI()

@app.post('/ingest-doc')
def main(files:list[UploadFile] = File(...)):
    file_info=[]
    for file in files:
        binary_content = file.file.read()
        io_bytes = io.ByteIO(binary_content)

        file_info.append({
            "stream":io_bytes,
            "file_name":file.filename
        })

    ingest(file_info)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )