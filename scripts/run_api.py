import os
import sys
import uvicorn
from pathlib import Path

src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.append(str(src_path))

from python_ocr.ftp.server import start_ftp_in_background
from python_ocr.core.config import settings

if __name__ == "__main__":
    ftp_thread = start_ftp_in_background()
    
    uvicorn.run(
        "python_ocr.api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )