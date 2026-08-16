from collections import deque
from dataclasses import dataclass, field
from time import monotonic
from typing import Any, Awaitable, Callable, Dict, Optional, Union

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from cachetools import TTLCache
from services.bot.text import TextService


EventType = Union[
    Message,
    CallbackQuery,
]

text = TextService()

@dataclass
class UserThrottleState:

    last_request: float = 0.0
    requests: deque = field(default_factory=lambda: deque(maxlen=21))
    ban_until: float = 0.0
    notified: bool = False


class ThrottlingMiddleware(BaseMiddleware):

    def __init__(
        self,
        debounce: float = 0.3,
        requests_limit: int = 20,
        interval: float = 30.0,
        ban_time: float = 30.0,
        cache_ttl: float = 300.0,
        max_users: int = 10000,
        throttle_message: Optional[str] = text("antispam"),
    ) -> None:

        self.debounce = debounce
        self.requests_limit = requests_limit
        self.interval = interval
        self.ban_time = ban_time
        self.throttle_message = throttle_message
        self.cache: TTLCache = TTLCache(maxsize=max_users, ttl=cache_ttl)

    async def __call__(
        self,
        handler: Callable[
            [EventType, Dict[str, Any]],
            Awaitable[Any],
        ],
        event: EventType,
        data: Dict[str, Any],
    ) -> Any:

        if event.from_user is None:
            return await handler(event, data)

        now = monotonic()
        user_id = event.from_user.id
        state = self.cache.get(user_id)

        if state is None:
            state = UserThrottleState()
            self.cache[user_id] = state

        # Пользователь забанен
        if now < state.ban_until:

            if (
                not state.notified
                and self.throttle_message
                and isinstance(event, Message)
            ):

                await event.answer(self.throttle_message)
                state.notified = True

            return None

        # Debounce
        if now - state.last_request < self.debounce:
            return None

        state.last_request = now

        # Очищаем старые запросы
        while state.requests and now - state.requests[0] > self.interval:
            state.requests.popleft()

        state.requests.append(now)

        # Антиспам
        if len(state.requests) > self.requests_limit:
            state.ban_until = now + self.ban_time
            state.notified = False

            if  self.throttle_message and isinstance(event, Message):
                await event.answer(self.throttle_message)
                state.notified = True

            return None

        return await handler(event, data)