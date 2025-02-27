from fastapi import APIRouter, Depends, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from app.core.dependencies import get_session
from app.core.templates import templates
from app.schemas import HabitForm
from app.services import (
    create_habit,
    delete_habit,
    get_active_habits,
    get_completed_habits,
    get_habit,
    update_habit,
)
from app.services.authentication import (
    authorize,
)
from app.settings import (
    ACCESS_TOKEN_NAME,
    HOST,
)

router = APIRouter(prefix='/webapp/{idx}', tags=['habit'])


@router.get('/home')
async def get_homepage(request: Request, idx: int = Path(...), session: AsyncSession = Depends(get_session)):
    """
    Главная страница со списком активных целей
    """

    user = await authorize(session=session, user_id=idx, token=request.cookies.get(ACCESS_TOKEN_NAME))
    if not user:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    habits = await get_active_habits(session=session, user_id=idx)

    return templates.TemplateResponse('main.html', {'request': request, 'host': HOST, 'user_id': idx, 'habits': habits})


@router.get('/completed')
async def get_completed(request: Request, idx: int = Path(...), session: AsyncSession = Depends(get_session)):
    """
    Страница со списком выполненных целей
    """

    user = await authorize(session=session, user_id=idx, token=request.cookies.get(ACCESS_TOKEN_NAME))
    if not user:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    habits = await get_completed_habits(session=session, user_id=idx)

    return templates.TemplateResponse(
        'main.html', {'request': request, 'host': HOST, 'user_id': idx, 'habits': habits, 'completed': True}
    )


@router.get('/habit')
async def get_habit_create_form(request: Request, idx: int = Path(...), session: AsyncSession = Depends(get_session)):
    """
    Получение формы добавления новой цели
    """

    user = await authorize(session=session, user_id=idx, token=request.cookies.get(ACCESS_TOKEN_NAME))
    if not user:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    return templates.TemplateResponse('habit_form.html', {'request': request, 'host': HOST, 'user_id': idx})


@router.post('/habit')
async def create(
    request: Request,
    form: HabitForm = Depends(HabitForm.as_form),
    idx: int = Path(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Обработка формы добавления новой цели
    """

    user = await authorize(session=session, user_id=idx, token=request.cookies.get(ACCESS_TOKEN_NAME))
    if not user:
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    form_data = form.model_dump()
    await create_habit(session=session, user_id=idx, habit_data=form_data)

    habits = await get_active_habits(session=session, user_id=idx)

    return templates.TemplateResponse('main.html', {'request': request, 'host': HOST, 'user_id': idx, 'habits': habits})


@router.get('/habit/{habit_id}')
async def get_habit_update_form(
    request: Request, idx: int = Path(...), habit_id: int = Path(...), session: AsyncSession = Depends(get_session)
):
    """
    Получение формы обновления цели
    """

    user = await authorize(session=session, user_id=idx, token=request.cookies.get(ACCESS_TOKEN_NAME))
    if not user:
        return Response(status_code=status.HTTP_403_FORBIDDEN)
    habit = await get_habit(session=session, user_id=idx, habit_id=habit_id)
    if not habit:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        'habit_form.html', {'request': request, 'host': HOST, 'user_id': idx, 'habit': habit}
    )


@router.post('/habit/{habit_id}')
async def update(
    request: Request,
    form: HabitForm = Depends(HabitForm.as_form),
    idx: int = Path(...),
    habit_id: int = Path(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Обработка формы обновления цели
    """

    user = await authorize(session=session, user_id=idx, token=request.cookies.get(ACCESS_TOKEN_NAME))
    if not user:
        return Response(status_code=status.HTTP_403_FORBIDDEN)
    habit = await get_habit(session=session, user_id=idx, habit_id=habit_id, active=True)
    if not habit:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    form_data = form.model_dump()
    habit = await update_habit(session=session, habit=habit, data=form_data)

    return templates.TemplateResponse(
        'habit_form.html', {'request': request, 'host': HOST, 'user_id': idx, 'habit': habit, 'success': True}
    )


@router.delete('/habit/{habit_id}')
async def delete(
    request: Request,
    idx: int = Path(...),
    habit_id: int = Path(...),
    session: AsyncSession = Depends(get_session),
) -> Response:
    """
    Удаление цели
    """

    user = await authorize(session=session, user_id=idx, token=request.cookies.get(ACCESS_TOKEN_NAME))
    if not user:
        return Response(status_code=status.HTTP_403_FORBIDDEN)
    habit = await get_habit(session=session, user_id=idx, habit_id=habit_id)
    if not habit:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    await delete_habit(session=session, habit=habit)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
