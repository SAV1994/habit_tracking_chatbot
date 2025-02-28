from fastapi import APIRouter, Depends, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from app.bot import bot
from app.core.dependencies import get_session
from app.core.templates import templates
from app.schemas import LoginForm, RegistrationForm
from app.services import get_active_habits, get_markup, get_user, set_user_password
from app.services.authentication import (
    authorize,
    check_password,
    generate_user_tokens,
)
from app.settings import (
    ACCESS_TOKEN_LIFETIME,
    ACCESS_TOKEN_NAME,
    HOST,
    REFRESH_TOKEN_NAME,
)

router = APIRouter(prefix='/webapp/{idx}', tags=['authentication'])


@router.get('/token')
async def set_new_tokens(request: Request, idx: int = Path(...), session: AsyncSession = Depends(get_session)):
    """
    Инициализация новой сессии пользователя с webapp посредством access-токена
    """

    user = await authorize(
        session=session, user_id=idx, token=request.query_params.get(REFRESH_TOKEN_NAME), use_refresh_token=True
    )
    if user:
        await generate_user_tokens(session=session, user=user)
        habits = await get_active_habits(session=session, user_id=idx)
        response = templates.TemplateResponse('main.html', {'request': request, 'user_id': idx, 'habits': habits})
        response.set_cookie(
            key=ACCESS_TOKEN_NAME, value=user.access_token, httponly=True, max_age=3600 * ACCESS_TOKEN_LIFETIME
        )

        await bot.send_message(
            user.id,
            text='❕ Новый вход в меню постановки целей.',
            disable_notification=False,
            reply_markup=get_markup(user),
        )
    else:
        response = Response(status_code=status.HTTP_403_FORBIDDEN)

    return response


@router.get('/register')
async def get_register_form(request: Request, idx: int = Path(...), session: AsyncSession = Depends(get_session)):
    """
    Получение формы регистрации пользователя
    """

    user = await get_user(session=session, user_id=idx)
    if not user or user.password:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    return templates.TemplateResponse('registration_form.html', {'request': request})


@router.post('/register')
async def register(
    request: Request,
    form: RegistrationForm = Depends(RegistrationForm.as_form),
    idx: int = Path(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Обработка формы регистрации пользователя
    """

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

    await bot.send_message(
        user.id,
        text='❕ Новый вход в меню постановки целей.',
        disable_notification=False,
        reply_markup=get_markup(user),
    )

    return response


@router.get('/login')
async def get_login_form(request: Request, idx: int = Path(...), session: AsyncSession = Depends(get_session)):
    """
    Получение формы входа пользователя
    """

    user = await get_user(session=session, user_id=idx)
    if not user or not user.password:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    return templates.TemplateResponse('login_form.html', {'request': request, 'error': False})


@router.post('/login')
async def login(
    request: Request,
    form: LoginForm = Depends(LoginForm.as_form),
    idx: int = Path(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Обработка формы входа пользователя
    """

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

        await bot.send_message(
            user.id,
            text='❕ Новый вход в меню постановки целей.',
            disable_notification=False,
            reply_markup=get_markup(user),
        )
    else:
        response = templates.TemplateResponse('login_form.html', {'request': request, 'user_id': idx, 'error': True})

    return response
