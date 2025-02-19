from telebot import types
from telebot.async_telebot import AsyncTeleBot

from app.services import get_markup
from app.settings import (
    BOT_TOKEN,
)

bot = AsyncTeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
async def start(message):
    extra_data = message.json['extra_data']
    user = extra_data['user']

    webapp = types.BotCommand(command='webapp', description='Редактировать цели')
    archive = types.BotCommand(command='archive', description='Список выполненных целей')
    mark_complete = types.BotCommand(command='mark_complete', description='Отметить выполнение')

    await bot.set_my_commands([webapp, archive, mark_complete])
    await bot.set_chat_menu_button(message.chat.id, types.MenuButtonCommands('commands'))

    await bot.send_message(
        message.chat.id,
        f'Здравствуйте, {user.name}. Я HabitBot. Давайте менять жизнь к лучшему вместе. 😉',
    )


@bot.message_handler(commands=['webapp'])
async def webapp(message):
    extra_data = message.json['extra_data']
    user = extra_data['user']

    await bot.send_message(
        message.chat.id,
        text='Вам нужно добавить новые цели или отредактировать существующие? Тогда кликайте по кнопке "Мои цели".',
        reply_markup=get_markup(user=user),
    )
