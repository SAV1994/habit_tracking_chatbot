from contextlib import asynccontextmanager

from apscheduler.triggers.cron import CronTrigger
from fastapi import APIRouter, FastAPI, Request
from pydantic_core import ValidationError
from starlette import status
from starlette.responses import JSONResponse

from app.database import Base, engine
from app.services import scheduler, summarize_daily_results
from app.settings import (
    HOST,
)
from app.webapp import authentication_router, habits_router, webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # before the application starts taking requests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    scheduler.start()
    scheduler.add_job(summarize_daily_results, trigger=CronTrigger(hour=15, minute=55))

    from app.bot import bot

    await bot.set_webhook(url=f'{HOST}/webhook')

    yield

    #  after the application finishes handling requests, right before the shutdown
    scheduler.shutdown()

    await bot.remove_webhook()


app = FastAPI(lifespan=lifespan)

router = APIRouter()

router.include_router(webhook_router)
router.include_router(authentication_router)
router.include_router(habits_router)

app.include_router(router)


@app.exception_handler(ValidationError)
def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': str(exc)})
