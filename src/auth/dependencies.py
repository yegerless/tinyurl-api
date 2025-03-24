from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .schemas import User, UserInDB


fake_users_db = {
    "johndoe": {
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "created_at": "2025-02-23 16:35:38.966",
        "last_login_at": "2025-02-23 16:35:38.966",
        "is_active": "True"
        
    }
}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
