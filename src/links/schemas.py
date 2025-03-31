import re
from datetime import datetime
from pydantic import BaseModel, Field


# Регулярка для валидации исходных ссылок 
valid_url_regexp = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class PostShortenLinkRequestBody(BaseModel):
    source_url: str = Field(pattern=valid_url_regexp, 
                             description='url, к которому будет привязана короткая ссылка', 
                             examples=['https://pikabu.ru',])
    custom_alias: str | None = Field(default=None, 
                                     description='Кастомный алиас для короткой ссылки',
                                     examples=['pika',])
    expires_at: str | None = Field(pattern=r'(\d{2}).(\d{2}).(\d{4}) (\d{2}):(\d{2})', default=None, 
                                   description='Дата и время удаления короткой ссылки', 
                                   examples=['12.06.2025 04:20',])



class UpdateShortLinkRequest(BaseModel):
    new_alias: str | None = Field(default=None, 
                                     description='Кастомный алиас для короткой ссылки',
                                     examples=['pkb'])
    expires_at: str | None = Field(pattern=r'(\d{2}).(\d{2}).(\d{4}) (\d{2}):(\d{2})', default=None, 
                                   description='Дата и время удаления короткой ссылки',
                                   examples=['10.04.2025 12:30']) 



class UrlData(BaseModel):
    user_id: int
    alias: str
    source_url: str
    created_at: datetime
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    transitions_quantity: int  = 0
