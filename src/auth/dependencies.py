from fastapi.security import APIKeyCookie


coockie_scheme = APIKeyCookie(name='tinyurl_access_token')
