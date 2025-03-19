import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = (os.getenv("DEBUG", "False") == 'True')
HOST_URL_OR_DOMEN = os.getenv("HOST_URL_OR_DOMEN")
HOST_PORT = os.getenv('HOST_PORT')