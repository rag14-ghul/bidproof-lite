import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings

def get_default_db_path() -> str:
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") or os.getenv("VERCEL_ENV"):
        return "/tmp/bidproof.db"
    return "data/bidproof.db"

class Settings(BaseSettings):
    APP_NAME: str = "BidProof-Lite"
    LLM_MODE: Literal["deterministic", "ollama", "hosted"] = "deterministic"
    LLM_FLOOR: float = 0.85
    OLLAMA_URL: str = "http://localhost:11434/v1"
    OLLAMA_MODEL: str = "qwen3:8b"
    HOSTED_URL: str = "https://api.openai.com/v1"
    HOSTED_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str = "mock-key"
    
    DB_PATH: str = get_default_db_path()
    SECRET_KEY: str = "bidproof-secret-session-key-demo-2026"
    BIDPROOF_DEMO_PASSWORD: str = "demo@123"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
