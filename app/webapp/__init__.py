from typing import Any, List

from .authentication import router as authentication_router
from .habit import router as habits_router
from .webhook import router as webhook_router

__all__: List[Any] = [authentication_router, habits_router, webhook_router]
