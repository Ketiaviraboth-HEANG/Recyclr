from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from logic import analyze_receipt, preprocess_image

app = FastAPI()


@app.post("/upload-receipt")
async def upload_receipt(file: UploadFile = File(...)):
    content = await file.read()
    data = analyze_receipt(content)
    return JSONResponse(content={"data": data})
