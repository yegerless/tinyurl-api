from fastapi import APIRouter

links_router = APIRouter(prefix='/links', tags=['links'])


@links_router.post('/shorten')
async def post_shorten_link():
    '''
        Создает кастомную короткую ссылку если передан параметр alias.
        Если ничего не передано, то генерирует alias автоматически и создает короткую ссылку.
        Если создается с параметром expires_at в формате даты с точностью до минуты, 
            то после указанного времени короткая ссылка автоматически удаляется.
    '''

    return {'message': 'ok'}


@links_router.get('/{short_code}')
async def redirect_on_full_link():
    '''
        Перенаправляет на оригинальный URL, который привязан к короткой ссылке.
    '''

    return {'message': 'short_link'}


@links_router.delete('/{short_code}')
async def delete_short_link():
    '''
        Удаляет пару короткая_ссылка-оригинальная_сслыка
    '''

    return {'message': 'link deleted'}


@links_router.put('/{short_code}')
async def update_short_link():
    '''
        Обновляет коротки адрес (принимает кастомный или генеруриет новый).
    '''

    return {'message': 'link updated'}


@links_router.get('/{short_code}/stats')
def get_short_link_statistics():
    '''
        Отображает оригинальный URL, возвращает дату создания, количество переходов, дату последнего использования.
    '''

    return {'message': 'statistics'}


@links_router.get('/search?original_url={url}')
def get_shotr_link_by_original_url():
    '''
        Возвращает короткую ссылку, привязанную к переданному оригинальному url
    '''

    return {'message': 'short_link'}