from typing import Annotated
from pydantic import BaseModel, Field, AfterValidator

from ..utils import valid_url_regexp


class PostShortenLinkRequestBody(BaseModel):
    source_link: str = Field(pattern=valid_url_regexp, 
                             description='url, к которому будет привязана короткая ссылка', 
                             examples=['https://pikabu.ru',])
    custom_alias: str | None = Field(default=None, 
                                     description='Кастомный алиас для короткой ссылки',
                                     examples=['pika'])
    expires_at: str | None = Field(default=None, 
                                   description='Дата и время удаления короткой ссылки')



class UpdateShortLinkRequest(BaseModel):
    custom_alias: str | None = Field(default=None, 
                                     description='Кастомный алиас для короткой ссылки',
                                     examples=['pika'])
    expires_at: str | None = Field(default=None, 
                                   description='Дата и время удаления короткой ссылки') 
