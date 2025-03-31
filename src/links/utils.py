import re
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache

from .models import Link
from .schemas import UrlData



def get_random_link_alias(short_code_lenght: int = 6):
    '''
        Принимает длину алиаса и создает случайный алиас для сокращенной ссылки при помощи функции uuid4.
        Аргументы:
            short_code_lenght (int): длина алиаса, по умолчанию 6.
    '''

    alias = str(uuid.uuid4())[:short_code_lenght]

    return alias


@cache(expire=60)
async def get_url_data_by_alias(alias: str, session: AsyncSession) -> str | bool:
    '''
        Функция get_url_by_alias
    '''

    query = select(Link).filter(Link.alias == alias)
    url = await session.execute(query)
    url = url.scalar()
    
    if not url:
        return False
    
    url_dict = {}
    url_dict['user_id'] = url.user_id
    url_dict['alias'] = url.alias
    url_dict['source_url'] = url.source_url
    url_dict['created_at'] = url.created_at
    url_dict['expires_at'] = url.expires_at
    url_dict['last_used_at'] = url.last_used_at
    url_dict['transitions_quantity'] = url.transitions_quantity

    return url_dict