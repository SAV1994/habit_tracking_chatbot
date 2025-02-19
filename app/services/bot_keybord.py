from telebot import types
from telebot.types import WebAppInfo

from app.models import User
from app.services.authentication import check_token
from app.settings import HOST, REFRESH_TOKEN_NAME


def get_markup(user: User) -> types.ReplyKeyboardMarkup:
    if not user.password:
        btn = types.KeyboardButton(text='Мои цели', web_app=WebAppInfo(url=HOST + f'webapp/{user.id}/register'))
    elif not check_token(user=user, token=user.refresh_token, refresh=True):
        btn = types.KeyboardButton(text='Мои цели', web_app=WebAppInfo(url=HOST + f'webapp/{user.id}/login'))
    else:
        btn = types.KeyboardButton(
            text='Мои цели',
            web_app=WebAppInfo(url=HOST + f'webapp/{user.id}/token?{REFRESH_TOKEN_NAME}={user.refresh_token}'),
        )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(btn)

    return markup
