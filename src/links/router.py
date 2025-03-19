from fastapi import APIRouter

from config import HOST_URL_OR_DOMEN, HOST_PORT
from .utils import get_random_link_alias
from .schemas.requests_schemas import PostShortenLinkRequestBody, ShortCode

links_router = APIRouter(prefix='/links', tags=['links'])


@links_router.post('/shorten')
async def post_shorten_link(link_params: PostShortenLinkRequestBody):
    '''
        Создает кастомную короткую ссылку если передан параметр alias.
        Если ничего не передано, то генерирует alias автоматически и создает короткую ссылку.
        Если создается с параметром expires_at в формате даты с точностью до минуты, 
            то после указанного времени короткая ссылка автоматически удаляется.
    '''

    link_params = link_params.dict()
    # Проверка, передан ли кастомный алиас для короткой ссылки
    if not link_params.get('custom_alias'):
        alias = get_random_link_alias()
        # ТУТ НУЖНА ПРОВЕРКА НЕТ ЛИ ТАКОГО АЛИАСА В БД
    else:
        alias = link_params.get('custom_alias')
        # ТУТ НУЖНА ПРОВЕРКА НЕТ ЛИ ТАКОГО АЛИАСА В БД

    expires_at = link_params.get('expires_at', 'NULL')

    'Здесь ссылка сохраняется в БД'

    response = {'message': 'Short link created.', 'short_link': f'{HOST_URL_OR_DOMEN}:{HOST_PORT}/links/{alias}'} 
    return response


@links_router.get('/{short_code}')
async def redirect_on_full_link(short_code: str):
    '''
        Перенаправляет на оригинальный URL, который привязан к короткой ссылке.
    '''

    return {'message': f'short_link: {short_code}'}


@links_router.delete('/{short_code}')
async def delete_short_link(short_code):
    '''
        Удаляет пару короткая_ссылка-оригинальная_сслыка
    '''

    return {'message': 'link deleted'}


@links_router.put('/{short_code}')
async def update_short_link(short_code):
    '''
        Обновляет коротки адрес (принимает кастомный или генеруриет новый).
    '''

    return {'message': 'link updated'}


@links_router.get('/{short_code}/stats')
def get_short_link_statistics(short_code):
    '''
        Отображает оригинальный URL, возвращает дату создания, количество переходов, дату последнего использования.
    '''

    return {'message': 'statistics'}


@links_router.get('/search')
def get_short_link_by_original_url(original_url):
    '''
        Возвращает короткую ссылку, привязанную к переданному оригинальному url
    '''

    return {'message': 'short_link'}