from datetime import datetime, timezone
from typing import Union

import jwt
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column, ForeignKey, Integer, String, Table, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, backref, joinedload, mapped_column, relationship

from app.config import (
    DATETIME_FORMAT,
    EXPIRE_ACCESS_TOKEN,
    EXPIRE_REFRESH_TOKEN,
    SECRET_PYJWT_ACCESS_KEY,
)
from app.core.utils import aware_now
from app.database import Base


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column('id', type_=Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column('username', type_=String)
    password: Mapped[str] = mapped_column('password', type_=String)
    first_name: Mapped[str] = mapped_column('first_name', type_=String)
    last_name: Mapped[str] = mapped_column('last_name', type_=String)
    access_token: Mapped[str] = mapped_column('access_token', type_=String)
    refresh_token: Mapped[str] = mapped_column('refresh_token', type_=String)

    @property
    def name(self):
        if self.first_name:
            name = self.first_name
            if self.last_name:
                name += f' {self.last_name}'
        else:
            name = self.username
        return name


async def get_user(session: AsyncSession, user_id: int) -> Union[User, None]:
    res = await session.execute(select(User).where(User.id == user_id))
    return res.unique().scalar_one_or_none()


async def get_or_create_user(session: AsyncSession, user_id: int, user_data: dict) -> User:
    user = await get_user(session=session, user_id=user_id)
    if not user:
        user = User(
            id=user_id,
            username=user_data.get('username', ''),
            password='',
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            access_token='',
            refresh_token='',
        )
        session.add(user)
        await session.commit()

    return user


async def set_user_password(session: AsyncSession, user: User, password: str) -> User:
    password_hash = pbkdf2_sha256.hash(password)
    user.password = password_hash

    expire_access_token = (aware_now() + EXPIRE_ACCESS_TOKEN).strftime(format=DATETIME_FORMAT)
    expire_refresh_token = (aware_now() + EXPIRE_REFRESH_TOKEN).strftime(format=DATETIME_FORMAT)

    user.access_token = jwt.encode(
        {'user_id': user.id, 'username': user.username, 'date': expire_access_token},
        SECRET_PYJWT_ACCESS_KEY,
        algorithm='HS256',
    )
    user.refresh_token = jwt.encode(
        {'user_id': user.id, 'username': user.username, 'date': expire_refresh_token},
        SECRET_PYJWT_ACCESS_KEY,
        algorithm='HS256',
    )

    await session.commit()
    await session.refresh(user)

    return user


#
# async def follow(session: AsyncSession, user: User, main_user_id: int) -> None:
#     main_user = await get_user(session=session, user_id=main_user_id)
#
#     if user in main_user.followers:
#         raise ValidationError('Пользователь уже подписан')
#
#     user.following.append(main_user)
#     await session.commit()
#
#
# async def unfollow(session: AsyncSession, user: User, main_user_id: int) -> None:
#     main_user = await get_user(session=session, user_id=main_user_id)
#
#     if user not in main_user.followers:
#         raise ValidationError('Пользователь не подписан')
#
#     user.following.remove(main_user)
#     await session.commit()
