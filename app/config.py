from datetime import timedelta
import os
from dotenv import load_dotenv
load_dotenv()


SECRET_PYJWT_ACCESS_KEY = os.getenv('SECRET_PYJWT_ACCESS_KEY')
SECRET_PYJWT_REFRESH_KEY = os.getenv('SECRET_PYJWT_REFRESH_KEY')
WEB_HOOK_URL = os.getenv('WEB_HOOK_URL')
BOT_TOKEN = os.getenv('BOT_TOKEN')

EXPIRE_ACCESS_TOKEN = timedelta(days=1)
EXPIRE_REFRESH_TOKEN = timedelta(days=7)
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'