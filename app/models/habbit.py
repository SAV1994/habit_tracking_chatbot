from typing import Sequence

from asyncpg.pgproto.pgproto import timedelta
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.utils import aware_now
from app.database import Base


class Habit(Base):
    __tablename__ = 'habit'

    id: Mapped[int] = mapped_column('id', type_=Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title: Mapped[str] = mapped_column('title', type_=String, nullable=False)
    description: Mapped[str] = mapped_column('description', type_=String, nullable=False)
    target: Mapped[int] = mapped_column('target', type_=Integer, default=21)
    process: Mapped[int] = mapped_column('process', type_=Integer, default=0)
    alert_time: Mapped[str] = mapped_column('alert_time', type_=Time, nullable=False)
    alert_date: Mapped[str] = mapped_column('alert_date', type_=Date, nullable=False)
    completed_date: Mapped[str] = mapped_column('completed_date', type_=DateTime, nullable=True)

    __table_args__ = (CheckConstraint(target > 0, name='check_target_positive'),)

    @property
    def days_left(self) -> int:
        return self.target - self.process


async def create_habit(session: AsyncSession, user_id: int, habit_data) -> None:
    habit = Habit(
        user_id=user_id,
        title=habit_data['title'],
        description=habit_data.get('description', ''),
        target=habit_data['target'],
        alert_time=habit_data['alert_time'],
        alert_date=(aware_now() + timedelta(days=1)).date(),
    )
    session.add(habit)
    await session.commit()


async def get_active_habits(session: AsyncSession, user_id: int) -> Sequence[Habit]:
    stmt = select(Habit).where(Habit.user_id == user_id, Habit.completed_date.is_(None))
    res = await session.execute(stmt)

    return res.scalars().all()
