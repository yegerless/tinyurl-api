from fastapi import HTTPException, status
from fastapi.security import APIKeyCookie



coockie_scheme = APIKeyCookie(name='tinyurl_access_token')

# Исключение, которое будет вызвано при провале валидации
credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail='Не удалось проверить учетные данные')
