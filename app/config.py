from datetime import timedelta
import os
from dotenv import load_dotenv
load_dotenv()


SECRET_PYJWT_ACCESS_KEY = os.getenv('SECRET_PYJWT_ACCESS_KEY')
SECRET_PYJWT_REFRESH_KEY = os.getenv('SECRET_PYJWT_REFRESH_KEY')

HOST = os.getenv('HOST')

BOT_TOKEN = os.getenv('BOT_TOKEN')
ACCESS_TOKEN_NAME = 'access-token'
REFRESH_TOKEN_NAME = 'refresh-token'
ACCESS_TOKEN_LIFETIME = 1  # hours
EXPIRE_ACCESS_TOKEN = timedelta(hours=ACCESS_TOKEN_LIFETIME)
EXPIRE_REFRESH_TOKEN = timedelta(hours=ACCESS_TOKEN_LIFETIME * 72)
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'