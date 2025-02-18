from typing import Union

import jwt
from jwt import DecodeError
from passlib.hash import pbkdf2_sha256
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import (
    DATETIME_FORMAT,
    EXPIRE_ACCESS_TOKEN,
    EXPIRE_REFRESH_TOKEN,
    SECRET_PYJWT_ACCESS_KEY,
    SECRET_PYJWT_REFRESH_KEY,
)
from app.core.utils import aware_now
from app.models import User, get_or_create_user


async def authenticate(session: AsyncSession, data: dict) -> User:
    if msg_data := data.get('message'):
        user_data = msg_data.get('from', {})
        if user_id := user_data.get('id'):
            user = await get_or_create_user(session=session, user_id=user_id, user_data=user_data)
            return user


async def generate_user_tokens(session: AsyncSession, user: User):
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
    password_hash = pbkdf2_sha256.hash(password)
    user.password = password_hash

    await generate_user_tokens(session=session, user=user)

    return user


def check_password(user: User, password: str) -> bool:
    return user and user.password and pbkdf2_sha256.verify(password, user.password)


def check_token(user_id: Union[int, str], token: str, secret_token: str) -> bool:
    try:
        token_data = jwt.decode(token, secret_token, algorithms=['HS256'])
        return token_data['date'] > aware_now().strftime(DATETIME_FORMAT) and token_data['user_id'] == int(user_id)
    except (DecodeError, KeyError, ValueError):
        return False
