import os
import requests
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Request, HTTPException, Depends
from fastapi.responses import JSONResponse

from ...core.config import settings
from ...core.security import verify_signature
from ...db.repositories.api_clients import get_api_client, update_usage_counter
from ...core.email import send_prediction_email
from ...schemas.api import PredictionResponse

router = APIRouter()

async def validate_api_auth(request: Request):
    api_key = request.headers.get("X-API-KEY")
    timestamp = request.headers.get("X-TIMESTAMP")
    signature = request.headers.get("X-SIGNATURE")
    
    if not all([api_key, timestamp, signature]):
        raise HTTPException(status_code=401, detail="Missing authentication headers")

    api_client = get_api_client(api_key)
    if not api_client:
        raise HTTPException(status_code=403, detail="Invalid API key")
        
    path = request.url.path
    if not verify_signature(api_client["apiSecret"], timestamp, path, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
        
    return api_client

@router.post("/ftp_upload_and_predict/", response_model=PredictionResponse)
async def ftp_upload_and_predict(
    file: UploadFile = File(...),
    email: Optional[str] = None,
    api_client = Depends(validate_api_auth)
):
    file_bytes = await file.read()

    try:
        response = requests.post(
            settings.MODEL_URL,
            files={"file": (file.filename, file_bytes, file.content_type)},
            data={"email": email or ""}
        )
        response.raise_for_status()
        prediction_result = response.json().get("prediction", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR proxy failed: {e}")

    if email:
        send_prediction_email(email, file.filename, prediction_result)

    update_usage_counter(api_client["idAPI"])

    return {
        "filename": file.filename,
        "prediction": prediction_result
    }