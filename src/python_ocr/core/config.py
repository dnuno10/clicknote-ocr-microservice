import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    MODEL_HOST: str = "127.0.0.1"
    MODEL_PORT: int = 8001
    MODEL_URL: str = f"http://{MODEL_HOST}:{MODEL_PORT}/predict"
    MAX_NEW_TOKENS: int = 100
    
    FTP_HOST: str = "127.0.0.1"
    FTP_PORT: int = 8021
    FTP_USER: str = "user"
    FTP_PASS: str = "pass"
    
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    RESEND_SENDER_EMAIL: str = os.getenv("RESEND_SENDER_EMAIL", "")
    
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Paths
    UPLOAD_DIR: str = "uploaded_images"
    
    class Config:
        env_file = ".env"

settings = Settings()