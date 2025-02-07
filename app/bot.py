from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Path, Request
from pydantic_core import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse, Response
from starlette.templating import Jinja2Templates
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.types import WebAppInfo

from app.config import BOT_TOKEN, WEB_HOOK_URL
from app.core.dependencies import get_session
from app.database import Base, engine
from app.models import get_user, set_user_password
from app.schemas import RegistrationForm
from app.services import authenticate

bot = AsyncTeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
async def start(message):
    markup = types.InlineKeyboardMarkup()
    login_btn = types.InlineKeyboardButton(
        text='login',
        web_app=WebAppInfo(url=WEB_HOOK_URL + f'{message.from_user.id}/register'),
    )
    register_btn = types.InlineKeyboardButton(text='register', callback_data='register#sdfsdfs;fksf')

    markup.row(login_btn, register_btn)
    # await bot.add_data(message.chat.id, key='fsfefsefsefsef')
    await bot.set_state(message.chat.id, state='fsfefsefsefsef')
    await bot.send_message(
        message.chat.id,
        'Вас приветствует HabitBot. Чтобы продолжить работу нужно зарегистрироваться.',
        reply_markup=markup,
    )


# @bot.message_handler(commands=['help', 'start'])
# async def menu(message):
#     keyboard = types.InlineKeyboardMarkup()

# @bot.message_handler(commands=['help', 'start'])
# async def menu(message):
#     keyboard = types.InlineKeyboardMarkup()
#     login_btn = types.InlineKeyboardButton(
#         text='login', web_app=types.WebAppInfo(url=WEB_HOOK_URL), start_parameter='fsdjfksdfl32423'
#     )
#     register_btn = types.InlineQueryResultsButton(
#         text='register', web_app=types.WebAppInfo(url=WEB_HOOK_URL), start_parameter='fsdjfksdfl32423'
#     )
#
#     keyboard.add(login_btn, register_btn)
#     # await bot.add_data(message.chat.id, key='fsfefsefsefsef')
#     await bot.set_state(message.chat.id, state='fsfefsefsefsef')
#     await bot.send_message(message.chat.id, 'button', reply_markup=keyboard)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('login'))
async def echo_message(callback):
    await bot.send_message(callback.message.chat.id, callback.data)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # before the application starts taking requests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await bot.set_webhook(url=WEB_HOOK_URL)

    yield

    #  after the application finishes handling requests, right before the shutdown
    await bot.remove_webhook()


app = FastAPI(lifespan=lifespan)


# if callback_query := data.get('callback_query'):
#     cmd, token = callback_query['data'].split('#')
#     callback_query['data'] = cmd


@app.post('/')
async def webhook(request: Request, session: AsyncSession = Depends(get_session)) -> None:
    data = await request.json()
    await authenticate(session=session, data=data)

    update = types.Update.de_json(data)

    await bot.process_new_updates([update])


templates = Jinja2Templates(directory='app/templates')


@app.get('/{idx}/register')
async def register_form(request: Request, idx: int = Path(...), session: AsyncSession = Depends(get_session)):
    user = await get_user(session=session, user_id=idx)
    if not user or user.password:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    response = templates.TemplateResponse('registration_form.html', {'request': request})
    return response


@app.post('/{idx}/register')
async def register(
    request: Request,
    form: RegistrationForm = Depends(RegistrationForm.as_form),
    idx: int = Path(...),
    session: AsyncSession = Depends(get_session),
):
    user = await get_user(session=session, user_id=idx)
    if not user or user.password:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    form_data = form.model_dump()
    user = await set_user_password(session=session, user=user, password=form_data['password'])

    response = templates.TemplateResponse('main.html', {'request': request, 'user_id': idx})
    response.set_cookie(key='access-token', value=user.access_token, httponly=True, max_age=86400)
    return response


@app.get('/{idx}/main')
async def webhook(request: Request, idx: int = Path(...)):
    return templates.TemplateResponse('main.html', {'request': request, 'user_id': idx})


@app.exception_handler(ValidationError)
def csrf_protect_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': str(exc)})
