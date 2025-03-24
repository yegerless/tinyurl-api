from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .dependencies import oauth2_scheme, get_current_user, fake_users_db, fake_hash_password, get_current_active_user
from .schemas import User, UserInDB

auth_router = APIRouter(prefix='/auth', tags=['auth'])

@auth_router.get('/items')
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {'token': token}


@auth_router.post('/tocken')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail='Некорректный email или пароль')
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail='Некорректный email или пароль')

    return {'access_token': user.username, "token_type": 'bearer'}


@auth_router.get('/users/me')
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user