from pydantic import BaseModel, EmailStr
from typing import Optional

class PredictionResponse(BaseModel):
    filename: str
    prediction: str

class ErrorResponse(BaseModel):
    detail: str