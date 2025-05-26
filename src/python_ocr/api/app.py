from fastapi import FastAPI
from .routers import prediction

def create_app() -> FastAPI:
    app = FastAPI(
        title="OCR API with TrOCR",
        description="Handwritten OCR service based on TrOCR + FastAPI + FTP",
        version="1.0.0"
    )

    app.include_router(prediction.router, prefix="/prediction", tags=["Prediction"])

    return app

app = create_app()