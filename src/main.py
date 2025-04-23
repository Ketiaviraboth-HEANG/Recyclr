import os

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from logic import analyze_receipt

app = FastAPI()


@app.post("/upload-receipt")
async def upload_receipt(file: UploadFile = File(...)):
    content = await file.read()
    data = analyze_receipt(content)
    return JSONResponse(content={"data": data})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("APP_PORT", 8000)))
