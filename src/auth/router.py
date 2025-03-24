from typing import Annotated
from datetime import timedelta, datetime, timezone
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from jwt import InvalidTokenError
from passlib.hash import bcrypt
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import fake_users_db, oauth2_scheme
from .schemas import Token, TokenData, SignUpUser
from .utils import authenticate_user, create_access_token, get_user
from .models import User
from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from database import get_async_session


auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.post('/signup')
async def signup(user_data: SignUpUser, session: AsyncSession = Depends(get_async_session)):
    email = user_data.email.lower()
    password = user_data.password

    if not password or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не передан email или пароль",
        )

    hashed_password = bcrypt.hash(password)
    created_at = datetime.now()
    last_login_at = None
    is_active = True

    new_user = User(email=email, hashed_password=hashed_password, created_at=created_at,
                    last_login_at=last_login_at, is_active=is_active)
    session.add(new_user)
    await session.commit()

    return new_user


@auth_router.post("/login")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                                 session: AsyncSession = Depends(get_async_session)) -> Token:

    user = await authenticate_user(User, form_data.username.lower(), form_data.password, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    query = update(User).filter(User.email == user.email).values(last_login_at=datetime.now())
    await session.execute(query)
    await session.commit()

    return Token(access_token=access_token, token_type="bearer")


@auth_router.get('/current-user')
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(User, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
