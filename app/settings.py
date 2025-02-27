import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('HOST')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Авторизация
SECRET_PYJWT_ACCESS_KEY = os.getenv('SECRET_PYJWT_ACCESS_KEY')
SECRET_PYJWT_REFRESH_KEY = os.getenv('SECRET_PYJWT_REFRESH_KEY')
ACCESS_TOKEN_NAME = 'access-token'
REFRESH_TOKEN_NAME = 'refresh-token'
ACCESS_TOKEN_LIFETIME = 1  # hours
EXPIRE_ACCESS_TOKEN = timedelta(hours=ACCESS_TOKEN_LIFETIME)
EXPIRE_REFRESH_TOKEN = timedelta(hours=ACCESS_TOKEN_LIFETIME * 72)

# Дата время
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TZ = 'Europe/Moscow'

# База данных
DATABASE_DETAILS = 'admin:admin@postgresql_container:5432'
DATABASE_URL_ASYNC = 'postgresql+asyncpg://' + DATABASE_DETAILS
DATABASE_URL_SYNC = 'postgresql+psycopg2://' + DATABASE_DETAILS

# Apscheduler
APSCHEDULER_CONFIG = {
    'apscheduler.jobstores.default': {'type': 'sqlalchemy', 'url': DATABASE_URL_SYNC},
    'apscheduler.timezone': TZ,
    'apscheduler.jobstore_retry_interval': 1,
    'apscheduler.misfire_grace_time': 1,
}
