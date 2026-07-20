from datetime import time

from aiogram import F, Router, types
from aiogram.types import CallbackQuery

from database.session import SessionLocal
from keyboards.all_inline_kbs import (
    get_settings_kb,
    get_settings_reminder_time_kb,
    get_settings_utc_offset_kb,
)
from services.user_service import UserService


settings_router = Router()


async def build_settings_text(
    user,
    success_text: str | None = None,
) -> str:
    """Формирует текст страницы настроек."""

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

    text = (
        "<b>Настройки</b>\n\n"
        f"🌍 Часовой пояс: {timezone_text}\n"
        f"⏰ Время напоминания: {user.reminder_time.strftime('%H:%M')}\n"
        f"🔔 Уведомления: {notifications_text}"
    )

    if success_text:
        text += f"\n\n{success_text}"

    return text


async def send_settings(
    message: types.Message,
):
    """Отправляет настройки новым сообщением."""

    async with SessionLocal() as session:
        user_service = UserService(session)
        user = await user_service.get_by_id(message.from_user.id)

    await message.answer(
        await build_settings_text(user),
        reply_markup=get_settings_kb(user.notifications_enabled),
    )


async def edit_settings(
    call: CallbackQuery,
    success_text: str | None = None,
):
    """Обновляет сообщение с настройками."""

    async with SessionLocal() as session:
        user_service = UserService(session)
        user = await user_service.get_by_id(call.from_user.id)

    await call.message.edit_text(
        await build_settings_text(user, success_text),
        reply_markup=get_settings_kb(user.notifications_enabled),
    )

    await call.answer()


@settings_router.message(F.text == "⚙️ Настройки")
async def get_settings(message: types.Message):
    """Открывает настройки пользователя."""

    await send_settings(message)


@settings_router.callback_query(F.data == "settings_utc_offset")
async def select_utc_offset(call: CallbackQuery):
    """Открывает выбор часового пояса."""

    await call.message.edit_text(
        "🌍 Укажите вашу разницу во времени с Москвой:",
        reply_markup=get_settings_utc_offset_kb(),
    )

    await call.answer()


@settings_router.callback_query(F.data.startswith("settings_msk_"))
async def update_utc_offset(call: CallbackQuery):
    """Изменяет часовой пояс пользователя."""

    msk_offset = int(call.data.removeprefix("settings_msk_"))
    utc_offset = msk_offset + 3

    async with SessionLocal() as session:
        user_service = UserService(session)

        user = await user_service.get_by_id(call.from_user.id)
        user_service.update_utc_offset(user, utc_offset)

        await session.commit()

    await edit_settings(call, "✅ Часовой пояс изменен.")


@settings_router.callback_query(F.data == "settings_reminder_time")
async def select_reminder_time(call: CallbackQuery):
    """Открывает выбор времени напоминания."""

    await call.message.edit_text(
        "⏰ Выберите удобное время для ежедневного напоминания:",
        reply_markup=get_settings_reminder_time_kb(),
    )

    await call.answer()


@settings_router.callback_query(F.data.startswith("settings_time_"))
async def update_reminder_time(call: CallbackQuery):
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
        f"✅ Время напоминания изменено на {reminder_time.strftime('%H:%M')}.",
    )


@settings_router.callback_query(F.data == "settings_notifications")
async def toggle_notifications(call: CallbackQuery):
    """Включает или отключает ежедневные уведомления."""

    async with SessionLocal() as session:
        user_service = UserService(session)

        user = await user_service.get_by_id(call.from_user.id)

        user_service.update_notifications_enabled(
            user,
            not user.notifications_enabled,
        )

        await session.commit()

    await edit_settings(
        call,
        (
            "✅ Уведомления включены."
            if user.notifications_enabled
            else "✅ Уведомления отключены."
        ),
    )


@settings_router.callback_query(F.data == "settings_back")
async def back_to_settings(call: CallbackQuery):
    """Возвращает пользователя в меню настроек."""

    await edit_settings(call)