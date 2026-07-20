from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data
from fastapi import Header, HTTPException

from config import BOT_TOKEN


async def get_telegram_init_data(
    authorization: str | None = Header(default=None),
) -> WebAppInitData:
    """Проверяет Telegram Mini App initData."""

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header отсутствует.",
        )

    scheme, _, init_data = authorization.partition(" ")

    if scheme.lower() != "tma" or not init_data:
        raise HTTPException(
            status_code=401,
            detail="Некорректный Authorization header.",
        )

    try:
        return safe_parse_webapp_init_data(
            token=BOT_TOKEN,
            init_data=init_data,
        )

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Некорректные Telegram initData.",
        )