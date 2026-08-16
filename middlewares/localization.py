from aiogram import BaseMiddleware

from services.bot.text import TextService


class LocalizationMiddleware(BaseMiddleware):

    def __init__(self, text: TextService):
        self.text = text

    async def __call__(
        self,
        handler,
        event,
        data,
    ):
        data["text"] = self.text

        return await handler(event, data)