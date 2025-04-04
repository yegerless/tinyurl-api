from datetime import datetime
from pydantic import BaseModel, Field, EmailStr



class SignUpUser(BaseModel):
    email: str
    password: str



class UserSchema(BaseModel):
    id: int 
    email: EmailStr = Field(description='Электронная почта пользователя')
    created_at: datetime = Field(description='Дата и время регистрации пользователя')
    last_login_at: datetime | None = Field(description='Дата и время последнего логина пользователя')
    is_active: bool = Field(description='Пользователь активен / не активен')



class UserInDB(UserSchema):
    hashed_password: str 



class Token(BaseModel):
    access_token: str
    token_type: str



class TokenData(BaseModel):
    username: str | None = None
