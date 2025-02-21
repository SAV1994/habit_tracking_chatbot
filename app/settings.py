import os
from datetime import timedelta

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
DATABASE_DETAILS = 'admin:admin@0.0.0.0:5450'
DATABASE_URL = 'postgresql+asyncpg://' + DATABASE_DETAILS
TZ = 'Europe/Moscow'
APSCHEDULER_CONFIG = {
    'apscheduler.jobstores.default': {'type': 'sqlalchemy', 'url': 'postgresql+psycopg2://' + DATABASE_DETAILS},
    'apscheduler.timezone': TZ,
    'apscheduler.jobstore_retry_interval': 1,
    'apscheduler.misfire_grace_time': 1,
}
