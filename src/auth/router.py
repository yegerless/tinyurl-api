from typing import Annotated
from datetime import timedelta, datetime
from fastapi import Depends, APIRouter, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from email_validator import validate_email, EmailNotValidError

from .dependencies import coockie_scheme, credentials_exception
from .utils import authenticate_user, create_access_token, get_user, validate_access_token, get_current_user
from .models import User, create_anonimous_user
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_async_session


create_anonimous_user()

auth_router = APIRouter(prefix='/auth', tags=['auth'])



@auth_router.post('/signup')
async def signup(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                 session: AsyncSession = Depends(get_async_session)) -> dict[str, str]:
    '''
        Принимает email и пароль, создает нового пользователя с username 
            соответствующим email и захешированным паролем в БД.
    '''

    # Парсинг и проверка email и пароля
    try:
        email = validate_email(form_data.username.lower()).normalized
    except EmailNotValidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))

    password = form_data.password
    if not password or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не передан email или пароль",
        )

    username = await get_user(User, session, email)
    if username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Пользователь с переданным email уже существует')

    # Хеширование пароля (для простоты сделал без соли)
    hashed_password = bcrypt.hash(password)

    # Создание информации о пользователе для заполнения дополнительных полей в БД
    created_at = datetime.now()
    last_login_at = None
    is_active = True

    # Создание записи о новом пользователе в БД
    new_user = User(email=email, hashed_password=hashed_password, created_at=created_at,
                    last_login_at=last_login_at, is_active=is_active)
    session.add(new_user)
    await session.commit()

    return {'message': f'Пользователь {new_user.email} зарегистрирован'}



@auth_router.post("/login")
async def login_for_access_token(response: Response, 
                                 form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                                 session: AsyncSession = Depends(get_async_session)) -> dict[str, str]:
    '''
        Принимает email и пароль, проверяет существование соответствующего пользователя, 
            а также совпадение переданного пароля с его хэшем в БД, генерирует JWT токен
            и сохраняет его в куках, возвращает сообщение об успешном залогинивании.
    '''

    # Загрузка инфы о пользователе из БД и проверка пароля
    user = await authenticate_user(User, form_data.username.lower(), form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Генерация JWT токена, установка времени его протухания
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, 
                                       expires_delta=access_token_expires)

    # Обновление записи в БД о дате и времени последнего залогинивания пользователя
    query = update(User).filter(User.email == user.email).values(last_login_at=datetime.now())
    await session.execute(query)
    await session.commit()

    # Установка сгенерированного JWT в куки
    response.set_cookie(key='tinyurl_access_token', value=access_token, 
                        expires=access_token_expires, httponly=True)

    return {'message': f'Пользователь {user.email} успешно залогинился'}



@auth_router.post('/logout')
async def logout(response: Response, session: AsyncSession = Depends(get_async_session), 
                 token: str = Depends(coockie_scheme)) -> dict[str, str]:
    '''
        Выполняет разлогин из системы путем удаления JWT из куки, 
            возвращает сообщение об успешном разлогинивании.
        Если пользователь не был залогинен, то возвращает ошибку 403.
    '''

    # Получение данных пользователя по токену, если токен не верный, 
    # то будет вызвано исключение
    user = await get_current_user(User, token, session)
    if not user:
        raise credentials_exception

    response.delete_cookie(key='tinyurl_access_token')
    return {'message': f'Пользователь {user.email} успешно разлогинился'}



@auth_router.get('/current-user')
async def get_current_user_data(token: Annotated[str, Depends(coockie_scheme)], 
                           session: AsyncSession = Depends(get_async_session)) -> dict[str, str]:
    '''
        Возвращает username и дату время последнего логина для текущего пользователя. 
    '''

    # Получение данных пользователя
    user = await get_current_user(User, token, session)
    if not user:
        raise credentials_exception

    return {'username': user.email, 'last_login_at': str(user.last_login_at)}
