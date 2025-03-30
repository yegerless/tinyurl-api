import os
from dotenv import load_dotenv

load_dotenv()

# Настройки приложения api
DEBUG = (os.getenv("DEBUG", "False") == 'True')
HOST_URL_OR_DOMEN = os.getenv("HOST_URL_OR_DOMEN")
HOST_PORT = int(os.getenv('HOST_PORT'))

# Настройки безопасности (для jwt токенов)
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

# Настройки подключения к PostgresQL
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_EXTERNAL_PORT = int(os.getenv('POSTGRES_EXTERNAL_PORT'))
POSTGRES_INTERNAL_PORT = int(os.getenv('POSTGRES_INTERNAL_PORT'))

# Настройки подключения к Redis
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
