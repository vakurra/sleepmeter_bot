from typing import Annotated
from datetime import time, datetime, timedelta, timezone

from aiogram.utils.web_app import WebAppInitData
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database.session import SessionLocal
from services.db.sleep import SleepService
from services.db.user import UserService
from web.auth import get_telegram_init_data
from web.schemas import UpdateProfileRequest


app = FastAPI(
    title="Somnus API",
)

app.mount(
    "/static",
    StaticFiles(directory="web/static"),
    name="static",
)


@app.get("/")
async def index():
    """Открывает Mini App."""

    return FileResponse("web/static/index.html")


@app.get("/api/health")
async def health():
    """Проверяет доступность API."""

    return {"status": "ok"}


@app.get("/api/profile")
async def get_profile(
    init_data: Annotated[
        WebAppInitData,
        Depends(get_telegram_init_data),
    ],
):
    """Возвращает профиль текущего пользователя."""

    if not init_data.user:
        raise HTTPException(
            status_code=401,
            detail="Telegram user отсутствует.",
        )

    async with SessionLocal() as session:
        user_service = UserService(session)

        user = await user_service.get_by_id(init_data.user.id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Пользователь не найден.",
            )

        return {
            "first_name": user.first_name,
            "username": user.username,
            "utc_offset": user.utc_offset,
            "reminder_time": user.reminder_time.strftime("%H:%M"),
            "notifications_enabled": user.notifications_enabled,
        }


@app.get("/api/statistics")
async def get_statistics(
    init_data: Annotated[
        WebAppInitData,
        Depends(get_telegram_init_data),
    ],
    days: int = 7,
):
    """Возвращает статистику сна текущего пользователя."""

    if days not in (7, 30):
        raise HTTPException(
            status_code=400,
            detail="Допустимые периоды: 7 или 30 дней.",
        )

    if not init_data.user:
        raise HTTPException(
            status_code=401,
            detail="Telegram user отсутствует.",
        )

    async with SessionLocal() as session:
        user_service = UserService(session)
        sleep_service = SleepService(session)

        user = await user_service.get_by_id(init_data.user.id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Пользователь не найден.",
            )

        local_datetime = (
            datetime.now(timezone.utc)
            + timedelta(hours=user.utc_offset)
        )

        date_to = local_datetime.date()
        date_from = date_to - timedelta(days=days - 1)

        records = await sleep_service.get_by_period(
            user_id=user.id,
            date_from=date_from,
            date_to=date_to,
        )

    total_duration = sum(
        record.sleep_duration
        for record in records
    )

    average_duration = (
        total_duration // len(records)
        if records
        else None
    )

    average_rating = (
        round(
            sum(record.sleep_rating for record in records)
            / len(records),
            2,
        )
        if records
        else None
    )

    return {
        "period_days": days,
        "filled_days": len(records),
        "average_duration": average_duration,
        "average_rating": average_rating,
        "records": [
            {
                "date": record.record_date.isoformat(),
                "sleep_start": record.sleep_start.strftime("%H:%M"),
                "sleep_end": record.sleep_end.strftime("%H:%M"),
                "sleep_duration": record.sleep_duration,
                "sleep_rating": record.sleep_rating,
            }
            for record in records
        ],
    }


@app.patch("/api/profile")
async def update_profile(
    request: UpdateProfileRequest,
    init_data: Annotated[
        WebAppInitData,
        Depends(get_telegram_init_data),
    ],
):
    if not init_data.user:
        raise HTTPException(401)

    async with SessionLocal() as session:
        user_service = UserService(session)

        user = await user_service.get_by_id(init_data.user.id)

        if not user:
            raise HTTPException(404)

        if request.utc_offset is not None:
            user_service.update_utc_offset(
                user,
                request.utc_offset,
            )

        if request.reminder_time is not None:
            hour, minute = map(
                int,
                request.reminder_time.split(":"),
            )

            user_service.update_reminder_time(
                user,
                time(hour, minute),
            )

        if request.notifications_enabled is not None:
            user_service.update_notifications_enabled(
                user,
                request.notifications_enabled,
            )

        await session.commit()

    return {"ok": True}