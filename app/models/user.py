from typing import Union

from sqlalchemy import Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

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
