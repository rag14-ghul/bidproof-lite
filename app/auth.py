import hashlib
from typing import Optional
from fastapi import Request, HTTPException, Depends

from app.config import settings

def hash_password(password: str) -> str:
    salt = b"bidproof_salt_2026"
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000).hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def get_current_user(request: Request) -> Optional[str]:
    return request.session.get("user")

def login_required(request: Request) -> str:
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user
