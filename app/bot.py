from telebot import types
from telebot.async_telebot import AsyncTeleBot

from app.services import get_actual_habits, get_completed_habits, get_markup, mark_habit
from app.settings import BOT_TOKEN

bot = AsyncTeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
async def start(message):
    """
    Инициализация бота
    """

    extra_data = message.json['extra_data']
    user = extra_data['user']

    webapp_cmd = types.BotCommand(command='webapp', description='Редактировать цели')
    archive_cmd = types.BotCommand(command='archive', description='Список завершённых целей')
    mark_cmd = types.BotCommand(command='mark', description='Отметить выполнение')

    await bot.set_my_commands([mark_cmd, webapp_cmd, archive_cmd])
    await bot.set_chat_menu_button(message.chat.id, types.MenuButtonCommands('commands'))

    await bot.send_message(
        message.chat.id,
        f'Здравствуйте, {user.name}. Я HabitBot. Давайте менять жизнь к лучшему вместе. 😉',
    )


@bot.message_handler(commands=['webapp'])
async def webapp(message):
    """
    Получение кнопки для доступа к webapp
    """

    extra_data = message.json['extra_data']
    user = extra_data['user']

    await bot.send_message(
        message.chat.id,
        text='Вам нужно добавить новые цели или отредактировать существующие? Тогда кликайте по кнопке "Мои цели".',
        reply_markup=get_markup(user=user),
    )


@bot.message_handler(commands=['archive'])
async def archive(message):
    """
    Список выработанных привычек
    """

    extra_data = message.json['extra_data']
    user = extra_data['user']
    session = extra_data['session']

    completed_habits = await get_completed_habits(session=session, user_id=user.id)
    if completed_habits:
        msg_items = [
            f'🏆 {i}. | {habit.completed_date} | {habit.title}' for i, habit in enumerate(completed_habits, start=1)
        ]
        msg = '\n'.join(msg_items)
    else:
        msg = '❌ Вы пока ещё не закончили работу над какими-либо привычками'

    await bot.send_message(message.chat.id, text=msg)


@bot.message_handler(commands=['mark'])
async def mark(message):
    """
    Список активных целей на день
    """

    extra_data = message.json['extra_data']
    user = extra_data['user']
    session = extra_data['session']

    actual_habits = await get_actual_habits(session=session, user_id=user.id)

    if actual_habits:
        markup = types.InlineKeyboardMarkup()

        buttons = [
            types.InlineKeyboardButton(text=habit.title, callback_data=f'habit#{habit.id}') for habit in actual_habits
        ]
        markup.add(*buttons)

        await bot.send_message(
            message.chat.id,
            text='Чтобы отметить выполнение, просто нажмите соответствующую кнопку',
            reply_markup=markup,
        )
    else:
        await bot.send_message(message.chat.id, text='У Вас нет целей на сегодня')


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('habit#'))
async def mark_habit_handler(callback):
    """
    Отметка о выполнении цели
    """

    extra_data = callback.json['extra_data']
    user = extra_data['user']
    session = extra_data['session']

    _, habit_id = callback.data.split('#')
    habit = await mark_habit(session=session, habit_id=int(habit_id), user_id=user.id)
    if habit and habit.completed_date:
        await bot.send_message(
            callback.message.chat.id, f'Поздравляем! 👏 Вы закончили работу над привычкой "{habit.title}". 💪'
        )
    elif habit:
        await bot.send_message(
            callback.message.chat.id, f'Вы выполнили цель по работе над привычкой "{habit.title}". Так держать! 👍'
        )
    else:
        await bot.send_message(callback.message.chat.id, '❗ Что-то пошло не так ')
