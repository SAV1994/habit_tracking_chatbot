from sqlalchemy.ext.asyncio import AsyncSession

from app.models import get_or_create_user, User


async def authenticate(session: AsyncSession, data: dict) -> User:
    if msg_data := data.get('message'):
        user_data = msg_data.get('from', {})
        if user_id := user_data.get('id'):
            user = await get_or_create_user(session=session, user_id=user_id, user_data=user_data)
            return user

async def authorize(session: AsyncSession, user_id, access_token) -> bool:
    ...