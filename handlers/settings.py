from datetime import time

from aiogram import F, Router
from aiogram.types import CallbackQuery, InputRichMessage, Message

from database.session import SessionLocal
from keyboards.inline.settings import (
    get_settings_kb,
    get_settings_reminder_time_kb,
    get_settings_utc_offset_kb,
)
from services.db.user import UserService
from services.bot.text import TextService


settings_router = Router()


def get_settings_table(user, text: TextService):
    
    msk_offset = user.utc_offset - 3

    if msk_offset == 0:
        timezone_text = "Москва"
    elif msk_offset > 0:
        timezone_text = f"Мск +{msk_offset}"
    else:
        timezone_text = f"Мск {msk_offset}"

    notifications_text = (
        "Включены"
        if user.notifications_enabled
        else "Выключены"
    )

    return text.table(
        "settings-table",
        header=False,
        striped=True,
        timezone=timezone_text,
        reminder_time=user.reminder_time.strftime("%H:%M"),
        notifications=notifications_text,
    )


async def send_settings(message: Message, text: TextService):
    async with SessionLocal() as session:
        user_service = UserService(session)
        user = await user_service.get_by_id(message.from_user.id)

    rich_message = InputRichMessage(
        blocks=[
            text.heading("settings-title"),
            get_settings_table(user, text),
        ],
    )

    await message.answer_rich(
        rich_message,
        reply_markup=get_settings_kb(user.notifications_enabled),
    )


async def edit_settings(call: CallbackQuery, text: TextService, success_text: str | None = None):
    
    async with SessionLocal() as session:
        user_service = UserService(session)
        user = await user_service.get_by_id(call.from_user.id)

    rich_message = InputRichMessage(
        blocks=[
            text.heading("settings-title"),
            get_settings_table(user, text),
        ],
    )

    await call.message.edit_text(
        rich_message=rich_message,
        reply_markup=get_settings_kb(user.notifications_enabled),
    )

    await call.answer(success_text)


@settings_router.message(F.text == "Настройки")
async def get_settings(message: Message, text: TextService):
    """Открывает настройки пользователя."""

    await send_settings(message, text)


@settings_router.callback_query(F.data == "settings_utc_offset")
async def select_utc_offset(call: CallbackQuery, text: TextService):
    """Открывает выбор часового пояса."""

    await call.message.edit_text(
        text("settings-utc-offset"),
        reply_markup=get_settings_utc_offset_kb(),
    )

    await call.answer()


@settings_router.callback_query(F.data.startswith("settings_msk_"))
async def update_utc_offset(call: CallbackQuery, text: TextService):
    """Изменяет часовой пояс пользователя."""

    msk_offset = int(call.data.removeprefix("settings_msk_"))
    utc_offset = msk_offset + 3

    async with SessionLocal() as session:
        user_service = UserService(session)
        user = await user_service.get_by_id(call.from_user.id)
        user_service.update_utc_offset(user, utc_offset)
        await session.commit()

    await edit_settings(call, text, text("settings-timezone-changed"))


@settings_router.callback_query(F.data == "settings_reminder_time")
async def select_reminder_time(call: CallbackQuery, text: TextService):
    """Открывает выбор времени напоминания."""

    await call.message.edit_text(
        text("settings-reminder-time"),
        reply_markup=get_settings_reminder_time_kb(),
    )

    await call.answer()


@settings_router.callback_query(F.data.startswith("settings_time_"))
async def update_reminder_time(call: CallbackQuery, text: TextService):
    """Изменяет время ежедневного напоминания."""

    selected_time = call.data.removeprefix("settings_time_")
    hour, minute = map(int, selected_time.split(":"))
    reminder_time = time(hour, minute)

    async with SessionLocal() as session:
        user_service = UserService(session)
        user = await user_service.get_by_id(call.from_user.id)
        user_service.update_reminder_time(user, reminder_time)
        await session.commit()

    await edit_settings(
        call,
        text,
        text(
            "settings-reminder-time-changed",
            time=reminder_time.strftime("%H:%M"),
        ),
    )


@settings_router.callback_query(F.data == "settings_notifications")
async def toggle_notifications(call: CallbackQuery, text: TextService):
    """Включает или отключает ежедневные уведомления."""

    async with SessionLocal() as session:
        user_service = UserService(session)
        user = await user_service.get_by_id(call.from_user.id)
        
        user_service.update_notifications_enabled(
            user,
            not user.notifications_enabled,
        )

        await session.commit()

    success_text = text(
        "settings-notifications-enabled"
        if user.notifications_enabled
        else "settings-notifications-disabled"
    )

    await edit_settings(call, text, success_text)


@settings_router.callback_query(F.data == "settings_back")
async def back_to_settings(call: CallbackQuery, text: TextService):
    """Возвращает пользователя в меню настроек."""

    await edit_settings(call, text)