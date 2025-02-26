from contextlib import asynccontextmanager

from apscheduler.triggers.cron import CronTrigger
from fastapi import APIRouter, FastAPI, Request
from pydantic_core import ValidationError
from starlette import status
from starlette.responses import JSONResponse

from app.services import scheduler, summarize_daily_results
from app.settings import (
    HOST,
)
from app.webapp import authentication_router, habits_router, webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.bot import bot

    # Запуск планировщика задач
    scheduler.start()
    # Запуск периодической задачи по подведению итогов за прошедший день
    scheduler.add_job(summarize_daily_results, trigger=CronTrigger(hour=00, minute=5))
    # Передача URL для webhook бота
    await bot.set_webhook(url=f'{HOST}/webhook')

    yield

    #  after the application finishes handling requests, right before the shutdown

    # Остановка планировщика задач
    scheduler.shutdown()
    # Отключаем webhook бота
    await bot.remove_webhook()


# Отключаем документирование, т.к. API не для внешнего пользования
app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


router = APIRouter()

router.include_router(webhook_router)
router.include_router(authentication_router)
router.include_router(habits_router)

app.include_router(router)


@app.exception_handler(ValidationError)
def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': str(exc)})
