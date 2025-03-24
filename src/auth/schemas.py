from pydantic import BaseModel, Field



class User(BaseModel):
    # email: str = Field(pattern='', description='Электронная почта пользователя')
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None



class UserInDB(User):
    hashed_password: str 
