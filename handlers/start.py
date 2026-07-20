from datetime import time

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto

from database.session import SessionLocal
from keyboards.all_inline_kbs import get_reminder_time_kb, get_utc_offset_kb
from keyboards.all_reply_kbs import start_reply_kb
from services.user_service import UserService


start_router = Router()


class UserRegistration(StatesGroup):
    """Регистрация нового пользователя."""

    utc_offset = State()
    reminder_time = State()


@start_router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):

    async with SessionLocal() as session:

        user_service = UserService(session)
        user = await user_service.get_by_id(message.from_user.id)

        if user:
            await message.answer(
                f"С возвращением, {message.from_user.first_name}!",
                reply_markup=start_reply_kb,
            )
            return

    await state.set_state(UserRegistration.utc_offset)
    timezone_photo = FSInputFile("assets/images/q1.png")
    await message.answer_photo(
        photo=timezone_photo,
        caption="Добро пожаловать, я Somnus!\n\n"
        "Я помогу отслеживать продолжительность вашего сна.\n\n"
        "Для начала потребуется всего две настройки.\n\n"
        "<b>Выберите разницу вашего времени с московским:</b>",
        reply_markup=get_utc_offset_kb("reg"),
    )


@start_router.callback_query(UserRegistration.utc_offset, F.data.startswith("reg_msk_"))
async def process_utc_offset(call: CallbackQuery, state: FSMContext):
    """Обработка выбора часового пояса."""

    moscow_offset = int(call.data.split("_")[-1])
    utc_offset = 3 + moscow_offset
    await state.update_data(utc_offset=utc_offset)
    await state.set_state(UserRegistration.reminder_time)

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile(
                "assets/images/q2.png"
            ),
            caption="<b>Когда вам удобно получать напоминание?</b>\n\n"
                    "<i>(Его можно будет отключить в настройках)</i>",
        ),
        reply_markup=get_reminder_time_kb("reg"),
    )

    await call.answer()


@start_router.callback_query(UserRegistration.reminder_time, F.data == "reg_back")
async def back_to_timezone(call: CallbackQuery, state: FSMContext):
    """Возврат к выбору часового пояса."""

    await state.set_state(UserRegistration.utc_offset)

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile(
                "assets/images/q1.png"
            ),
            caption="<b>Укажите вашу разницу во времени с Москвой:</b>",
        ),
        reply_markup=get_utc_offset_kb("reg"),
    )

    await call.answer()


@start_router.callback_query(UserRegistration.reminder_time, F.data.startswith("reg_time_"))
async def process_reminder_time(call: CallbackQuery, state: FSMContext):
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
        )

    await state.clear()

    await call.message.edit_caption(
        caption=(
            "✅ Регистрация завершена!\n\n"
            "Теперь я буду ежедневно присылать напоминание "
            "в выбранное время."
        ),
        reply_markup=None,
    )

    await call.message.answer(
        "Чем займемся?",
        reply_markup=start_reply_kb,
    )

    await call.answer()
