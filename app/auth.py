import hashlib
from typing import Optional
from fastapi import Request, HTTPException, status
from app.config import settings

def hash_password(password: str) -> str:
    return hashlib.sha256((password + settings.SECRET_KEY).encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def get_current_user(request: Request) -> Optional[str]:
    return request.cookies.get("bidproof_user")

def login_required(request: Request) -> str:
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    return user
