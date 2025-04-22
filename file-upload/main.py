import uvicorn
import mimetypes
from fastapi import FastAPI,File,UploadFile
from fastapi.responses import FileResponse,StreamingResponse

app = FastAPI()

def iter_file(filename:str):
    with open(filename,'rb') as file:
        while chunk := file.read(1024*1024):
            yield chunk

def get_mime_type(filename: str) -> str:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'

@app.post('/upload',tags=['File upload'])
async def upload_file(uploaded_file:UploadFile):
    file = uploaded_file.file
    filename = uploaded_file.filename
    with open(f'1{filename}','wb') as f:
        f.write(file.read())

@app.get('/download_file/{filename}',tags=['File upload'])
def download_file(filename:str):
    return FileResponse(filename)

@app.get('/download_file/streaming/{filename}',tags=['File upload'])
def download_file_stream(filename:str):
    mime_type = get_mime_type(filename)
    return StreamingResponse(iter_file(filename),media_type=mime_type)

if __name__ == '__main__':
    uvicorn.run('main:app',reload=True)