from typing import Annotated
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import UserInDB, TokenData, User
from .dependencies import oauth2_scheme, fake_users_db
from config import SECRET_KEY, ALGORITHM
from database import get_async_session


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password, hashed_password):
    '''
        Принимает пароль и хеш пароля и сравнивает их.
    '''

    return pwd_context.verify(plain_password, hashed_password)


async def get_user(user_table, session: AsyncSession, username: str):

    query = select(user_table).filter(user_table.email == username)
    result = await session.execute(query)
    result = result.scalars().all()
    user_dict = {}
    for user_obj in result:
        user_dict['email'] = user_obj.email
        user_dict['created_at'] = user_obj.created_at
        user_dict['last_login_at'] = user_obj.last_login_at
        user_dict['is_active'] = user_obj.is_active
        user_dict['hashed_password'] = user_obj.hashed_password

    return UserInDB(**user_dict)


async def authenticate_user(user_table, username: str, password: str, session: AsyncSession):

    user = await get_user(user_table, session, username)

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail='Не удалось проверить учетные данные',
                                          headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Неактивный пользователь')
    return current_user
