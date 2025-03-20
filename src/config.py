import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = (os.getenv("DEBUG", "False") == 'True')
HOST_URL_OR_DOMEN = os.getenv("HOST_URL_OR_DOMEN")
HOST_PORT = os.getenv('HOST_PORT')

POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')