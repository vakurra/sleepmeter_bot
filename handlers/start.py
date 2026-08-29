from datetime import time

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message

from services.bot.text import TextService
from database.session import SessionLocal
from keyboards.inline.registration import get_reminder_time_kb, get_utc_offset_kb
from keyboards.reply.start_menu import start_reply_kb
from services.db.user import UserService
from services.db.ad import AdService


start_router = Router()


class UserRegistration(StatesGroup):
    """Регистрация нового пользователя."""

    utc_offset = State()
    reminder_time = State()


@start_router.message(Command("start"))
async def start_command(message: Message, state: FSMContext, text: TextService):
    async with SessionLocal() as session:
        user_service = UserService(session)
        user = await user_service.get_by_id(message.from_user.id)
        name = message.from_user.first_name

        if user:
            await message.answer(
                text("start-return", name=name),
                reply_markup=start_reply_kb,
            )
            return

        referred_by = None

        if message.text:
            parts = message.text.split(maxsplit=1)

            if len(parts) == 2:
                campaign_name = parts[1].strip()

                ad_service = AdService(session)
                ad = await ad_service.get_by_campaign_name(campaign_name)

                if ad:
                    referred_by = ad.campaign_name

    await state.update_data(referred_by=referred_by)
    await state.set_state(UserRegistration.utc_offset)

    timezone_photo = FSInputFile("assets/images/q1.png")

    await message.answer_photo(
        photo=timezone_photo,
        caption=text("start-welcome", name=name),
        reply_markup=get_utc_offset_kb("reg"),
    )


@start_router.callback_query(UserRegistration.utc_offset, F.data.startswith("reg_msk_"))
async def process_utc_offset(call: CallbackQuery, state: FSMContext, text: TextService):
    """Обработка выбора часового пояса."""

    moscow_offset = int(call.data.split("_")[-1])
    utc_offset = 3 + moscow_offset
    await state.update_data(utc_offset=utc_offset)
    await state.set_state(UserRegistration.reminder_time)

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile("assets/images/q2.png"),
            caption=text("start-reminder"),
        ),
        reply_markup=get_reminder_time_kb("reg"),
    )

    await call.answer()


@start_router.callback_query(UserRegistration.reminder_time, F.data == "reg_back")
async def back_to_timezone(call: CallbackQuery, state: FSMContext, text: TextService):
    """Возврат к выбору часового пояса."""

    await state.set_state(UserRegistration.utc_offset)
    name = call.from_user.first_name

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile("assets/images/q1.png"),
            caption=text("start-welcome", name=name),
        ),
        reply_markup=get_utc_offset_kb("reg"),
    )

    await call.answer()


@start_router.callback_query(UserRegistration.reminder_time, F.data.startswith("reg_time_"))
async def process_reminder_time(call: CallbackQuery, state: FSMContext, text: TextService):
    """Завершение регистрации."""

    selected_time = call.data.removeprefix("reg_time_")
    hour, minute = map(int, selected_time.split(":"))
    reminder_time = time(hour, minute)
    data = await state.get_data()

    async with SessionLocal() as session:

        user_service = UserService(session)

        await user_service.create(
            tg_user=call.from_user,
            utc_offset=data["utc_offset"],
            reminder_time=reminder_time,
            referred_by=data["referred_by"],
        )

    await state.clear()

    await call.message.edit_caption(
        caption=text("start-complete-registration"),
        reply_markup=None,
    )

    await call.message.answer(text("start-whats-next"), reply_markup=start_reply_kb)
    await call.answer()
