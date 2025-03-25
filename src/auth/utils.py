from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import UserInDB, TokenData
from config import SECRET_KEY, ALGORITHM


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password, hashed_password) -> bool:
    '''
        Функция verify_password - принимает пароль и хеш пароля 
            и сравнивает их, возвращает True, если пароль и его 
            хэш совпали, в противном случае False.
        Аргументы:
            plain_password (str) - пароль.
            hashed_password (str) - хэш пароля.
        
    '''

    return pwd_context.verify(plain_password, hashed_password)



async def get_user(user_table, session: AsyncSession, username: str) -> UserInDB | bool:
    '''
        Функция get_user - принимает объект таблицы в БД, сесси. подключения 
            к БД и имя пользователя, возвращает валидированный объект с 
            данными пользовател из БД (UserInDB).
        Аргументы:
            user_table - объект таблицы (sqlalchemy) с данными пользователей.
            session (AsyncSession) - сессия подключения к БД.
            username (str) - имя пользователя, которого требуется найти в БД.
    '''

    # Формирование запроса к БД и получение данных
    query = select(user_table).filter(user_table.email == username)
    result = await session.execute(query)
    result = result.scalars().all()

    # Проверка, что пользователь существует
    if not result:
        return False

    # Парсинг полученных данных в словарь
    user_dict = {}
    for user_obj in result:
        user_dict['email'] = user_obj.email
        user_dict['created_at'] = user_obj.created_at
        user_dict['last_login_at'] = user_obj.last_login_at
        user_dict['is_active'] = user_obj.is_active
        user_dict['hashed_password'] = user_obj.hashed_password

    return UserInDB(**user_dict)



async def authenticate_user(user_table, username: str, password: str, 
                            session: AsyncSession) -> bool | UserInDB:
    '''
        Функция authenticate_user - принимает объект таблицы (sqlalchemy) в БД,
            имя пользователя и его пароль, а также сессию подключение к БД. 
            Производит аутентификацию пользователя и возвращает объект 
            данных о пользователе в случае успеха или False в противном
            случае.
        Аргументы:
            user_table - объект таблицы (sqlalchemy) с данными пользователей.
            username (str) - имя пользователя для аутентификации.
            password (str) - пароль пользователя для аутентификации.
            session (AsyncSession) - сессия подключения к БД.
    '''

    # Получение объекта пользователя из БД и проверка его существования
    user = await get_user(user_table, session, username)
    if not user:
        return False

    # Проверка совпадения пароля и хэша пароля
    if not verify_password(password, user.hashed_password):
        return False

    return user



def create_access_token(data: dict, expires_delta: timedelta | None 
                        = timedelta(minutes=5)) -> str:
    '''
        Функция create_access_token - принимает словарь с данными и 
            время жизни токена, возвращает сгенерированный JWT токен.
        Аргументы:
            data (dict) - словарь с данными пользователя, по которым будет 
                сгенерирован JWT токен.
            expires_delta (timedelta или None) - время до протухания токена,
                по умолчанию 5 минут.
    '''

    # Создение копии данных для кодирования в JWT
    to_encode = data.copy()

    # Установка даты и времени протухания JWT токена
    # и ее добавление к данным для кодирования
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({'exp': expire})

    # Генерация JWT токена
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt



def validate_access_token(token: str) -> str:
    '''
        Функция validate_access_token - принимает JWT токен, декодирует 
            и валидирует его, возвращает имя пользователя, которому 
            принадлежит JWT токен.
        Аргументы:
            token (str) - JWT токен.
    '''

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        return False 

    username = payload.get("sub")

    return username



async def get_current_user(user_table, token: str, session: AsyncSession) -> UserInDB:
    '''
        Функция get_current_user - принимает объект таблицы (sqlalchemy) в БД,
            JWT токен пользователя и объект сессии подключения к БД. 
            Проверяет и декодирует JWT токен, проверяет существование 
            соответствующего пользователя и возвращает объект данных о пользователе.
        Аргументы:
            user_table - объект таблицы (sqlalchemy) с данными пользователей.
            token (str) - JWT токен.
            session (AsyncSession) - сессия подключения к БД.
    '''

    # Исключение, которое будет вызвано при провале валидации
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail='Не удалось проверить учетные данные',
                                          headers={"WWW-Authenticate": "Bearer"})

    # Получение и проверка username
    username = validate_access_token(token)
    if not username:
        raise credentials_exception
    token_data = TokenData(username=username)
    
    # Получение и проверка объекта с данными пользователя из БД
    user = await get_user(user_table, session=session, username=token_data.username)
    if not user:
        raise credentials_exception

    return user
