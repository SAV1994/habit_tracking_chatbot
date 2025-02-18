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

from app.config import (
    ACCESS_TOKEN_LIFETIME,
    ACCESS_TOKEN_NAME,
    BOT_TOKEN,
    HOST,
    REFRESH_TOKEN_NAME,
    SECRET_PYJWT_ACCESS_KEY,
    SECRET_PYJWT_REFRESH_KEY,
)
from app.core.dependencies import get_session
from app.database import Base, engine
from app.models import create_habit, get_user
from app.models.habbit import get_active_habits
from app.schemas import HabitForm, LoginForm, RegistrationForm
from app.services import authenticate, set_user_password
from app.services.authentication import (
    check_password,
    check_token,
    generate_user_tokens,
)

bot = AsyncTeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
async def start(message):
    extra_data = message.json['extra_data']
    user = extra_data['user']

    webapp = types.BotCommand(command='webapp', description='Редактировать цели')
    archive = types.BotCommand(command='archive', description='Список выполненных целей')
    active = types.BotCommand(command='active', description='Отметить выполнение')
    inactive = types.BotCommand(command='inactive', description='Взять в работу')

    await bot.set_my_commands([webapp, archive, active, inactive])
    await bot.set_chat_menu_button(message.chat.id, types.MenuButtonCommands('commands'))

    await bot.send_message(
        message.chat.id,
        f'Здравствуйте, {user.name}. Я HabitBot. Давайте менять жизнь к лучшему вместе. 😉',
    )


@bot.message_handler(commands=['webapp'])
async def webapp(message):
    extra_data = message.json['extra_data']
    user = extra_data['user']

    if not user.password:
        btn = types.KeyboardButton(text='Мои цели', web_app=WebAppInfo(url=HOST + f'{message.from_user.id}/register'))
    elif not check_token(user_id=user.id, token=user.refresh_token, secret_token=SECRET_PYJWT_REFRESH_KEY):
        btn = types.KeyboardButton(text='Мои цели', web_app=WebAppInfo(url=HOST + f'{message.from_user.id}/login'))
    else:
        btn = types.KeyboardButton(
            text='Мои цели',
            web_app=WebAppInfo(url=HOST + f'{message.from_user.id}/token?{REFRESH_TOKEN_NAME}={user.refresh_token}'),
        )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(btn)

    await bot.send_message(
        message.chat.id,
        text='Вам нужно добавить новые цели или отредактировать существующие? Тогда кликайте по кнопке "Мои цели".',
        reply_markup=markup,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # before the application starts taking requests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await bot.set_webhook(url=f'{HOST}/webhook')

    yield

    #  after the application finishes handling requests, right before the shutdown
    await bot.remove_webhook()


app = FastAPI(lifespan=lifespan)


# TODO: Скорее всего будет нужен HTTPS
@app.middleware('http')
async def add_process_authorization(request: Request, call_next):
    path_elements = str(request.url).split('/')
    endpoint = path_elements[-1]
    print(request.headers)
    if endpoint not in ['register', 'login', 'webhook'] and not endpoint.startswith('token?refresh-token='):
        user_id = path_elements[-2]
        access_token = request.cookies.get(ACCESS_TOKEN_NAME, None)
        if not check_token(user_id=user_id, token=access_token, secret_token=SECRET_PYJWT_ACCESS_KEY):
            return Response(status_code=status.HTTP_403_FORBIDDEN)

    response = await call_next(request)

    return response


@app.post('/webhook')
async def webhook(request: Request, session: AsyncSession = Depends(get_session)) -> None:
    data = await request.json()
    user = await authenticate(session=session, data=data)

    extra_data = {'user': user}
    data['message']['extra_data'] = extra_data
    update = types.Update.de_json(data)

    await bot.process_new_updates([update])


templates = Jinja2Templates(directory='app/templates')


@app.get('/{idx}/token')
async def set_new_tokens(request: Request, idx: int = Path(...), session: AsyncSession = Depends(get_session)):
    user = await get_user(session=session, user_id=idx)
    refresh_token = request.query_params.get(REFRESH_TOKEN_NAME, None)
    if check_token(user_id=idx, token=refresh_token, secret_token=SECRET_PYJWT_REFRESH_KEY):
        await generate_user_tokens(session=session, user=user)
        habits = await get_active_habits(session=session, user_id=idx)
        response = templates.TemplateResponse('main.html', {'request': request, 'user_id': idx, 'habits': habits})
        response.set_cookie(
            key=ACCESS_TOKEN_NAME, value=user.access_token, httponly=True, max_age=3600 * ACCESS_TOKEN_LIFETIME
        )
    else:
        response = Response(status_code=status.HTTP_403_FORBIDDEN)

    return response


@app.get('/{idx}/register')
async def get_register_form(request: Request, idx: int = Path(...), session: AsyncSession = Depends(get_session)):
    user = await get_user(session=session, user_id=idx)
    if not user or user.password:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

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
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    form_data = form.model_dump()
    user = await set_user_password(session=session, user=user, password=form_data['password'])

    habits = await get_active_habits(session=session, user_id=idx)
    response = templates.TemplateResponse('main.html', {'request': request, 'user_id': idx, 'habits': habits})
    response.set_cookie(
        key=ACCESS_TOKEN_NAME, value=user.access_token, httponly=True, max_age=3600 * ACCESS_TOKEN_LIFETIME
    )
    return response


@app.get('/{idx}/login')
async def get_login_form(request: Request, idx: int = Path(...), session: AsyncSession = Depends(get_session)):
    user = await get_user(session=session, user_id=idx)
    if not user or not user.password:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    response = templates.TemplateResponse('login_form.html', {'request': request, 'error': False})

    return response


@app.post('/{idx}/login')
async def login(
    request: Request,
    form: LoginForm = Depends(LoginForm.as_form),
    idx: int = Path(...),
    session: AsyncSession = Depends(get_session),
):
    user = await get_user(session=session, user_id=idx)
    if not user or not user.password:
        return Response(status_code=status.HTTP_403_FORBIDDEN)
    form_data = form.model_dump()
    if check_password(user=user, password=form_data['password']):
        await generate_user_tokens(session=session, user=user)

        habits = await get_active_habits(session=session, user_id=idx)
        response = templates.TemplateResponse(
            'main.html', {'request': request, 'host': HOST, 'user_id': idx, 'habits': habits}
        )
        response.set_cookie(
            key=ACCESS_TOKEN_NAME, value=user.access_token, httponly=True, max_age=3600 * ACCESS_TOKEN_LIFETIME
        )
    else:
        response = templates.TemplateResponse('login_form.html', {'request': request, 'user_id': idx, 'error': True})

    return response


@app.get('/{idx}/main')
async def get_homepage(request: Request, idx: int = Path(...), session: AsyncSession = Depends(get_session)):
    habits = await get_active_habits(session=session, user_id=idx)
    return templates.TemplateResponse('main.html', {'request': request, 'host': HOST, 'user_id': idx, 'habits': habits})


@app.get('/{idx}/add-habit')
async def get_habit_create_form(request: Request, idx: int = Path(...)):
    return templates.TemplateResponse('habit_form.html', {'request': request, 'host': HOST, 'user_id': idx})


@app.post('/{idx}/add-habit')
async def add_habit(
    request: Request,
    form: HabitForm = Depends(HabitForm.as_form),
    idx: int = Path(...),
    session: AsyncSession = Depends(get_session),
):
    user = await get_user(session=session, user_id=idx)
    if not user or not user.password:
        return Response(status_code=status.HTTP_403_FORBIDDEN)
    form_data = form.model_dump()
    await create_habit(session=session, user_id=idx, habit_data=form_data)

    habits = await get_active_habits(session=session, user_id=idx)
    response = templates.TemplateResponse(
        'main.html', {'request': request, 'host': HOST, 'user_id': idx, 'habits': habits}
    )
    return response


@app.exception_handler(ValidationError)
def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': str(exc)})
