import os
from pydantic_settings import BaseSettings

def get_default_db_path() -> str:
    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
        return "/tmp/bidproof.db"
    return os.path.join("data", "bidproof.db")

class Settings(BaseSettings):
    APP_NAME: str = "BidProof-Lite"
    SECRET_KEY: str = "sih-2026-bidproof-secret-key-super-secure"
    BIDPROOF_DEMO_PASSWORD: str = "demo@123"
    DB_PATH: str = get_default_db_path()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
