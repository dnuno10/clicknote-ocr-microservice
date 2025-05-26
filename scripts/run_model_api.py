import os
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.append(str(src_path))

from python_ocr.models.inference import infer_page
from python_ocr.core.config import settings

app = FastAPI(title="Local OCR Model API")

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    save_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    with open(save_path, "wb") as f:
        f.write(await file.read())
    
    try:
        prediction = infer_page(save_path)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
    return {"filename": file.filename, "prediction": prediction}

if __name__ == "__main__":
    uvicorn.run(
        "run_model_api:app",
        host=settings.MODEL_HOST, 
        port=settings.MODEL_PORT
    )