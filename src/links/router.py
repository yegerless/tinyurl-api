import time
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Query, Path, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from config import HOST_URL_OR_DOMEN, HOST_PORT
from database import get_async_session
from .utils import get_random_link_alias, get_url_data_by_alias
from .schemas import PostShortenLinkRequestBody, valid_url_regexp, UpdateShortLinkRequest
from .models import Link
from auth.models import User
from auth.dependencies import coockie_scheme, credentials_exception
from auth.utils import get_current_user

links_router = APIRouter(prefix='/links', tags=['links'])



@links_router.post('/shorten')
async def post_shorten_link(request: Request, link_params: PostShortenLinkRequestBody, 
                            session: AsyncSession = Depends(get_async_session)) -> dict[str, str]:
    '''
        Создает кастомную короткую ссылку если передан параметр alias.
        Если ничего не передано, то генерирует alias автоматически и создает короткую ссылку.
        Если создается с параметром expires_at в формате даты с точностью до минуты, 
            то после указанного времени короткая ссылка автоматически удаляется.
    '''

    # Получение JWT токена и проверка, авторизован ли пользователь
    token = request.cookies.get('tinyurl_access_token')
    user = await get_current_user(User, token, session)
    if user:
        user_id = user.get('id')
    else:
        user_id = 1    # Идентификатор для неавторизованного пользователя

    # Распаковка тела запроса
    link_params = link_params.dict()
    source_url = link_params.get('source_url')
    
    # Проверка, передан ли кастомный алиас для короткой ссылки
    if not link_params.get('custom_alias'):
        # Генерация случайной короткой ссылки длиной в 6 символов
        alias = get_random_link_alias()
        # Если был сгененрирован уже существующий алиас, 
        # то генерирует новый алиас длиной 7 символов
        url = await get_url_data_by_alias(alias, session)
        if url:
            alias = get_random_link_alias(7)
    else:
        alias = link_params.get('custom_alias')
        url = await get_url_data_by_alias(alias, session)
        # Если переданный алиас уже существует, то возвращает ошибку 409
        if url:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='Переданный custom_alias уже существует')

    # Парсинг времени удаления ссылки
    expires_at = link_params.get('expires_at')
    if expires_at:
        expires_at = time.strptime(expires_at, '%d.%m.%Y %H:%M')
        expires_at = time.mktime(expires_at)
        expires_at = datetime.fromtimestamp(expires_at)

    # Установка значений дополнительных данных о ссылке
    created_at = datetime.now()
    last_used_at = None
    transitions_quantity = 0

    # Сохранение записи о ссылке в БД
    new_link = Link(user_id=user_id, alias=alias, source_url=source_url,
                    created_at=created_at, expires_at=expires_at,
                    last_used_at=last_used_at, 
                    transitions_quantity=transitions_quantity)
    session.add(new_link)
    await session.commit()

    return {'message': 'Короткая ссылка успешно создана.', 
            'short_link': f'{HOST_URL_OR_DOMEN}:{HOST_PORT}/links/{alias}'} 



@links_router.get('/search')
@cache(expire=60)
async def get_short_link_by_original_url(original_url: Annotated[str, Query(regexp=valid_url_regexp)], 
                                         request: Request, 
                                         session: AsyncSession = Depends(get_async_session)) -> dict[str, str]:
    '''
        Возвращает короткую ссылку, привязанную к переданному оригинальному url.
        Авторизованный пользователь получит данные только о своих ссылках.
        Неавторизованный пользователь получит данные только о тех ссылках,
            которые были созданы неавторизованными пользователями.
    '''

    # Получение JWT токена и проверка, авторизован ли пользователь
    token = request.cookies.get('tinyurl_access_token')
    user = await get_current_user(User, token, session)
    if user:
        user_id = user.get('id')
    else:
        user_id = 1    # Идентификатор для неавторизованного пользователя

    # Получение данных о ссылке из БД
    query = select(Link).filter((Link.source_url == original_url) & (Link.user_id == user_id))
    result = await session.execute(query)
    result = result.scalars().all()

    # Если данные о ссылке не найдены, вернется ошибка
    if len(result) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Для переданного original_url не найдены короткие ссылки.')

    # Список коротких ссылок, привязанных к переданному алиасу
    result = [f'{HOST_URL_OR_DOMEN}:{HOST_PORT}/links/{link_data.alias}' for link_data in result]

    return {'message': f'Найдено {len(result)} котортких ссылок для {original_url}',
            'shotr_codes_list': result}



@links_router.get('/{short_code}/stats')
async def get_short_link_statistics(short_code: Annotated[str, Path(description='Алиас короткой ссылки')],
                                    session: AsyncSession = Depends(get_async_session)):
    '''
        Отображает оригинальный URL, возвращает дату создания, количество переходов, дату последнего использования.
    '''

    # Получение данных о ссылке, если данные не найдены, то вернет ошику
    url = await get_url_data_by_alias(short_code, session)
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Переданный short_code не найден')

    return {'message': f'Найдены следующие статистики по короткой ссылке {HOST_URL_OR_DOMEN}:{HOST_PORT}/links/{short_code}',
            'original_url': url.get('source_url'), 'created_at': url.get('created_at'),
            'transitions_quantity': url.get('transitions_quantity'),
            'last_used_at': url.get('last_used_at')}



@links_router.get('/all_my_links')
async def get_all_my_links(token: str = Depends(coockie_scheme), 
                           session: AsyncSession = Depends(get_async_session)):
    '''
        Возвращает словарь со всеми короткими ссылками, которые создал пользователь
            в формате {short_code: original_url}.
        Эндпоинт доступен только залогиненным пользователям.
    '''

    # Получение данных о пользователе
    user = await get_current_user(User, token, session)
    if not user:
        raise credentials_exception

    # Получение данных о коротких ссылках, созданных пользователем
    query = select(Link).filter(Link.user_id == user.get('id'))
    result = await session.execute(query)
    result = result.scalars().all()

    # Если ни одной ссылки не найдено, вернет ошибку
    if len(result) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Для переданного original_url не найдены короткие ссылки.')

    # Сборка словаря со всеми ссылками пользователя в формате {short_code: original_url}
    result = {f'{HOST_URL_OR_DOMEN}:{HOST_PORT}/links/{link_data.alias}': 
                link_data.source_url for link_data in result}

    return {'message': 'Найдены следующие короткие ссылки',
            'links_dict': result}



@links_router.get('/{short_code}')
async def redirect_on_full_link(short_code: Annotated[str, Path(description='Алиас короткой ссылки')],
                                session: AsyncSession = Depends(get_async_session)):
    '''
        Перенаправляет на оригинальный URL, который привязан к короткой ссылке.
    '''

    # Получение данных о ссылке, если ссылка не найдена, то вернет ошибку
    url = await get_url_data_by_alias(short_code, session)
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Переданный short_code не найден')

    # Увеличение счетчика переходов по короткой ссылке на 1
    transitions_quantity = url.get('transitions_quantity') + 1
    query = update(Link).filter(Link.alias == short_code).values(last_used_at=datetime.now(),
                                                                 transitions_quantity=transitions_quantity)
    await session.execute(query)
    await session.commit()

    return RedirectResponse(url.get('source_url'))



@links_router.delete('/{short_code}')
async def delete_short_link(short_code: Annotated[str, Path(description='Алиас короткой ссылки')],
                            token: str = Depends(coockie_scheme),
                            session: AsyncSession = Depends(get_async_session)) -> dict[str, str]:
    '''
        Удаляет запись о короткой ссылке из БД.
        Эта ручка доступна только авторизованным пользователям.
        Пользователь может удалять только созданные им ссылки.
    '''

    # Получение данных о пользователе
    user = await get_current_user(User, token, session)
    if not user:
        raise credentials_exception

    # Удаление ссылки
    query = delete(Link).filter((Link.alias == short_code) & (Link.user_id == user.get('id')))
    await session.execute(query)
    await session.commit()

    return {'message': f'Ссылка {HOST_URL_OR_DOMEN}:{HOST_PORT}/links/{short_code} удалена'}



@links_router.put('/{short_code}')
async def update_short_link(short_code: Annotated[str, Path(description='Алиас короткой ссылки')],
                            link_params: UpdateShortLinkRequest,
                            token: str = Depends(coockie_scheme),
                            session: AsyncSession = Depends(get_async_session)):
    '''
        Обновляет короткий адрес (принимает кастомный или генеруриет новый).
        Перед обновлением проверяет, что исходный адрес принадлежит
            пользователю, который отправил запрос.
        Эта ручка доступна только авторизованным пользователям.
    '''

    # Получение данных пользователя и короткой ссылки из БД
    user = await get_current_user(User, token, session)
    url = await get_url_data_by_alias(short_code, session)

    # Проверка, что ссылка существует и принадлежит текущему пользователю
    if url.get('user_id') != user.get('id'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Указанный short_code принадлежит \
                                другому пользователю или не существует')

    # Распаковка тела запроса
    link_params = link_params.dict()

    # Проверка, передан ли кастомный алиас для короткой ссылки
    new_alias = link_params.get('new_alias')
    if not new_alias:
        # Генерация случайной короткой ссылки длиной в 6 символов
        new_alias = get_random_link_alias()
        # Если был сгененрирован уже существующий алиас, 
        # то генерирует новый алиас длиной 7 символов
        url = await get_url_data_by_alias(new_alias, session)
        if url:
            new_alias = get_random_link_alias(7)
    else:
        url = await get_url_data_by_alias(new_alias, session)
        # Если переданный алиас уже существует, то возвращает ошибку 409
        if url:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='Переданный new_alias уже существует')

    # Парсинг времени протухания ссылки
    expires_at = link_params.get('expires_at')
    if expires_at:
        expires_at = time.strptime(expires_at, '%d.%m.%Y %H:%M')
        expires_at = time.mktime(expires_at)
        expires_at = datetime.fromtimestamp(expires_at)

    query = update(Link).filter(Link.alias == short_code).values(alias=new_alias,
                                                                 expires_at=expires_at)

    await session.execute(query)
    await session.commit()
    return {'message': f'Ссылка изменена',
            'old_short_link' : f'{HOST_URL_OR_DOMEN}:{HOST_PORT}/links/{short_code}',
            'new_short_link': f'{HOST_URL_OR_DOMEN}:{HOST_PORT}/links/{new_alias}'}
