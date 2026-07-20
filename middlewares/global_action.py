from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from constants.global_actions import GLOBAL_ACTIONS


class GlobalActionMiddleware(BaseMiddleware):
    """Сбрасывает FSM при переходе к глобальному действию."""

    async def __call__(
        self,
        handler: Callable[
            [Message, dict[str, Any]],
            Awaitable[Any],
        ],
        event: Message,
        data: dict[str, Any],
    ) -> Any:

        if event.text in GLOBAL_ACTIONS:
            state: FSMContext = data["state"]

            if await state.get_state() is not None:
                await state.clear()

                data["raw_state"] = None

        return await handler(event, data)