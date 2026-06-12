from fastapi import FastAPI, File, UploadFile
import uvicorn

app = FastAPI()

@app.post('/ingest-doc')
def main(file: UploadFile = File(...)):
    print(file)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True, 
        reload_excludes=[".venv/*"]
    )