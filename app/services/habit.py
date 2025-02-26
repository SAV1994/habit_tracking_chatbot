from datetime import timedelta
from typing import Sequence, Union

from sqlalchemy import (
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import aware_now
from app.models import Habit
from app.services.notification import (
    add_job_by_datetime,
    delete_job,
    update_job_datetime,
)


async def create_habit(session: AsyncSession, user_id: int, habit_data: dict) -> Habit:
    """
    Добавление новой цели
    """

    habit = Habit(
        user_id=user_id,
        title=habit_data['title'],
        description=habit_data.get('description', ''),
        target=habit_data['target'],
        alert_time=habit_data['alert_time'],
        alert_date=aware_now().date(),
    )
    session.add(habit)
    await session.commit()

    await session.refresh(habit)

    add_job_by_datetime(habit=habit)

    return habit


async def update_habit(session: AsyncSession, habit: Habit, data: dict) -> Habit:
    """
    Обновление новой цели
    """

    alert_time_old = habit.alert_time

    for field in ['title', 'description', 'target', 'alert_time']:
        setattr(habit, field, data.get(field, ''))

    if alert_time_old != habit.alert_time:
        now = aware_now()
        if now.date() == habit.alert_date:
            if habit.alert_time < now.time() < alert_time_old:

                from app.bot import bot

                await bot.send_message(
                    chat_id=habit.user_id,
                    text=f'❗ В связи с изменением времени уведомления для привычки "{habit.title}", '
                    f'напоминание, ранее назначенное на сегодня на {alert_time_old}, не будет отправлено.',
                )
            elif habit.alert_time > now.time():
                update_job_datetime(habit=habit)

    await session.commit()

    return habit


async def get_habit(session: AsyncSession, user_id: int, habit_id: int, active: bool = False) -> Union[Habit, None]:
    """
    Получение цели по идентификатору
    """

    stmt = select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id)
    if active:
        stmt = stmt.where(Habit.completed_date.is_(None))
    res = await session.execute(stmt)

    return res.scalars().one_or_none()


async def get_active_habits(session: AsyncSession, user_id: int) -> Sequence[Habit]:
    """
    Получение активных целей (целей в работе)
    """

    stmt = select(Habit).where(Habit.user_id == user_id, Habit.completed_date.is_(None))
    res = await session.execute(stmt)

    return res.scalars().all()


async def get_completed_habits(session: AsyncSession, user_id: int) -> Sequence[Habit]:
    """
    Получение выполненных целей
    """

    stmt = select(Habit).where(Habit.user_id == user_id, Habit.completed_date.is_not(None))
    res = await session.execute(stmt)

    return res.scalars().all()


async def get_actual_habits(session: AsyncSession, user_id: int) -> Sequence[Habit]:
    """
    Получение активных целей на сегодняшний день
    """

    aware_date = aware_now().date()

    stmt = select(Habit).where(Habit.user_id == user_id, Habit.alert_date == aware_date)
    res = await session.execute(stmt)

    return res.scalars().all()


async def delete_habit(session: AsyncSession, habit: Habit) -> None:
    """
    Удаление цели
    """

    delete_job(habit=habit)

    await session.delete(habit)
    await session.commit()


async def mark_habit(session: AsyncSession, habit_id: int, user_id: int) -> Union[Habit, None]:
    """
    Отметка о выполнении дневной цели
    """

    aware_date = aware_now().date()

    stmt = select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id, Habit.alert_date == aware_date)
    res = await session.execute(stmt)
    if habit := res.scalars().one_or_none():
        habit.process += 1
        if habit.process == habit.target:
            habit.completed_date = aware_date
            habit.alert_date = None
            delete_job(habit=habit)
        else:
            habit.alert_date = aware_date + timedelta(days=1)
            update_job_datetime(habit=habit)
        await session.commit()

        return habit
