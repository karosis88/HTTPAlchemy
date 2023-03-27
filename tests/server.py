from fastapi import FastAPI
from fastapi import Request
from fastapi import UploadFile

app = FastAPI()


@app.get("/")
@app.post("/")
async def root():
    return 200


@app.post("/echo_body")
async def echo_body(req: Request):
    return await req.body()


@app.post("/file_upload")
async def upload_file(file: UploadFile):
    return file.size


@app.post("/files_upload")
async def upload_files(file: UploadFile, file1: UploadFile):
    return file.size + file1.size


@app.get("/echo_headers")
async def echo_headers(req: Request):
    return req.headers


@app.get("/json_url")
async def json(data: dict):
    return data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, port=7575)
