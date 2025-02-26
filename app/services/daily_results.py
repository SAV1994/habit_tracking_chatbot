from datetime import timedelta

from sqlalchemy import select

from app.core.utils import aware_now
from app.database import async_session
from app.models import Habit
from app.services.notification import update_job_datetime


async def summarize_daily_results() -> None:
    """
    Перенос невыполненных дневных целей
    """

    async with async_session() as session:
        aware_date = aware_now().date() - timedelta(days=1)

        stmt = select(Habit).where(Habit.alert_date == aware_date)
        res = await session.execute(stmt)
        unmarked_habits = res.scalars().all()
        for habit in unmarked_habits:
            habit.alert_date += timedelta(days=1)
            habit.process = 0

            from app.bot import bot

            await bot.send_message(
                chat_id=habit.user_id,
                text=f'❌ Не выполнена цель по привычке "{habit.title}". Счётчик сброшен. '
                f'В Следующий раз у Вас обязательно получится. ✊',
            )

            update_job_datetime(habit=habit)
        await session.commit()
