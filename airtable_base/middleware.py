from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from .fetch import AirtableActions


class AirtableMiddleware(BaseMiddleware):
    def __init__(self, connection: AirtableActions) -> None:
        self.connection = connection

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:

        data['air_connect'] = self.connection
        return await handler(event, data)