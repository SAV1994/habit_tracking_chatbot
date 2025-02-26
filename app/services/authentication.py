from typing import Union

import jwt
from jwt import DecodeError
from passlib.hash import pbkdf2_sha256
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import aware_now
from app.models import User
from app.services.user import get_or_create_user, get_user
from app.settings import (
    DATETIME_FORMAT,
    EXPIRE_ACCESS_TOKEN,
    EXPIRE_REFRESH_TOKEN,
    SECRET_PYJWT_ACCESS_KEY,
    SECRET_PYJWT_REFRESH_KEY,
)


async def authenticate(session: AsyncSession, data: dict) -> Union[User, None]:
    """
    Аутентификация пользователя, по данным полученным от Телеграм
    """

    if (msg_data := data.get('message')) or (msg_data := data.get('callback_query')):
        user_data = msg_data.get('from', {})
        if user_id := user_data.get('id'):
            return await get_or_create_user(session=session, user_id=user_id, user_data=user_data)


async def authorize(
    session: AsyncSession, user_id: int, token: Union[str, None], use_refresh_token: bool = False
) -> Union[User, None]:
    """
    Авторизация пользователя для работы с webapp
    """

    user = await get_user(session=session, user_id=user_id)
    if user and token:
        if check_token(user=user, token=token, refresh=use_refresh_token):
            return user


async def generate_user_tokens(session: AsyncSession, user: User) -> None:
    """
    Генерация токенов пользователя для доступа к webapp
    """

    expire_access_token = (aware_now() + EXPIRE_ACCESS_TOKEN).strftime(format=DATETIME_FORMAT)
    expire_refresh_token = (aware_now() + EXPIRE_REFRESH_TOKEN).strftime(format=DATETIME_FORMAT)

    user.access_token = jwt.encode(
        {'user_id': user.id, 'username': user.username, 'date': expire_access_token},
        SECRET_PYJWT_ACCESS_KEY,
        algorithm='HS256',
    )
    user.refresh_token = jwt.encode(
        {'user_id': user.id, 'username': user.username, 'date': expire_refresh_token},
        SECRET_PYJWT_REFRESH_KEY,
        algorithm='HS256',
    )
    await session.commit()

    await session.refresh(user)


async def set_user_password(session: AsyncSession, user: User, password: str) -> User:
    """
    Установка пароля пользователем
    """

    password_hash = pbkdf2_sha256.hash(password)
    user.password = password_hash

    await generate_user_tokens(session=session, user=user)

    return user


def check_password(user: User, password: str) -> bool:
    """
    Проверка пароля пользователя
    """

    return bool(user and user.password and pbkdf2_sha256.verify(password, user.password))


def check_token(user: User, token: str, refresh: bool = False) -> bool:
    """
    Проверка токена пользователя

    refresh=true - проверка refresh-токена
    refresh=false - проверка access-токена
    """

    if refresh:
        secret_token = SECRET_PYJWT_REFRESH_KEY
        token_from_db = user.refresh_token
    else:
        secret_token = SECRET_PYJWT_ACCESS_KEY
        token_from_db = user.access_token

    try:
        token_data = jwt.decode(token, secret_token, algorithms=['HS256'])
        return (
            token_data['date'] > aware_now().strftime(DATETIME_FORMAT)
            and token_data['user_id'] == user.id
            and token == token_from_db
        )
    except (DecodeError, KeyError, ValueError):
        return False
