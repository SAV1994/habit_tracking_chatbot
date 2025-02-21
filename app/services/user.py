from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def get_user(session: AsyncSession, user_id: Union[int, str]) -> Union[User, None]:
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
