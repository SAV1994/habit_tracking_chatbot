import datetime

import pytz
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from telebot import types

from app.models import Habit
from app.settings import APSCHEDULER_CONFIG, TZ

scheduler = AsyncIOScheduler(gconfig=APSCHEDULER_CONFIG)


async def alert(chat_id, habit_title, habit_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=habit_title, callback_data=f'habit#{habit_id}'))
    from app.bot import bot

    await bot.send_message(
        chat_id=chat_id,
        text=f'⚠ Напоминаем о необходимости закрепить привычку "{habit_title}". '
        'Чтобы отметить выполнение нажмите на кнопку ниже. У Вас всё получиться. 😉',
        reply_markup=markup,
    )


def get_job_id(user_id: int, habit_id: int):
    return f'{user_id}#{habit_id}'


def get_job_trigger_by_habit(habit: Habit) -> DateTrigger:
    return DateTrigger(
        run_date=datetime.datetime(
            year=habit.alert_date.year,
            month=habit.alert_date.month,
            day=habit.alert_date.day,
            hour=habit.alert_time.hour,
            minute=habit.alert_time.minute,
        ),
        timezone=pytz.timezone(TZ),
    )


def add_job_by_datetime(habit: Habit) -> None:
    scheduler.add_job(
        func=alert,
        trigger=get_job_trigger_by_habit(habit=habit),
        kwargs={'chat_id': habit.user_id, 'habit_title': habit.title, 'habit_id': habit.id},
        id=get_job_id(user_id=habit.user_id, habit_id=habit.id),
    )


def update_job_datetime(habit: Habit) -> None:
    try:
        scheduler.reschedule_job(
            job_id=get_job_id(user_id=habit.user_id, habit_id=habit.id),
            trigger=get_job_trigger_by_habit(habit=habit),
        )
    except JobLookupError:
        pass


def delete_job(habit: Habit) -> None:
    try:
        scheduler.remove_job(job_id=get_job_id(user_id=habit.user_id, habit_id=habit.id))
    except JobLookupError:
        pass
