from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from telebot import types

from app.bot import bot
from app.core.dependencies import get_session
from app.services import authenticate

router = APIRouter(prefix='/webhook', tags=['webhook'])


@router.post('')
async def webhook(request: Request, session: AsyncSession = Depends(get_session)) -> None:
    """
    Endpoint для webhook-ов от Telegram client
    """

    data = await request.json()
    user = await authenticate(session=session, data=data)

    extra_data = {'user': user, 'session': session}
    # Обработка обычных сообщений
    if message := data.get('message'):
        message['extra_data'] = extra_data
    # Обработка обычных событий вызванных callback-кнопками
    elif callback_query := data.get('callback_query'):
        callback_query['extra_data'] = extra_data
    update = types.Update.de_json(data)

    await bot.process_new_updates([update])
