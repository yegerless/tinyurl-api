from datetime import datetime
from pydantic import BaseModel, Field



class SignUpUser(BaseModel):
    email: str
    password: str



class User(BaseModel):
    email: str = Field( #pattern='', 
                       description='Электронная почта пользователя')
    created_at: datetime = Field(description='Дата и время регистрации пользователя')
    last_login_at: datetime | None = Field(description='Дата и время последнего логина пользователя')
    is_active: bool = Field(description='Пользователь активен / не активен')



class UserInDB(User):
    hashed_password: str 



class Token(BaseModel):
    access_token: str
    token_type: str



class TokenData(BaseModel):
    username: str | None = None
