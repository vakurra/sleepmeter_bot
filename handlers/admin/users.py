from aiogram import F, Router
from aiogram.types import CallbackQuery, InputRichMessage, Message

from database.session import SessionLocal
from keyboards.inline.admin_users import get_admin_users_kb
from middlewares.admin import AdminMiddleware
from services.bot.text import TextService
from services.db.user import UserService


admin_users_router = Router()

admin_users_router.message.middleware(AdminMiddleware())
admin_users_router.callback_query.middleware(AdminMiddleware())


def build_users_text(
    users,
    text: TextService,
    title_key: str,
    **kwargs,
) -> InputRichMessage:
    """Формирует Rich Message со списком пользователей."""

    rows = [
        f"{user.first_name or 'Без имени'} | "
        f"@{user.username or 'нет'} | "
        f"{user.created_at:%d.%m.%Y}"
        for user in users
    ]

    return InputRichMessage(
        blocks=[
            text.heading(
                title_key,
                size=3,
                **kwargs,
            ),
            text.table(
                "admin-users-table",
                header=True,
                striped=True,
                rows="\n".join(rows),
            ),
        ],
    )


@admin_users_router.message(F.text == "Пользователи")
async def show_users(
    message: Message,
    text: TextService,
):
    """Открывает меню пользователей."""

    await message.answer_rich(
        InputRichMessage(
            blocks=[
                text.heading(
                    "admin-users-title",
                    size=3,
                ),
            ],
        ),
        reply_markup=get_admin_users_kb(),
    )


@admin_users_router.callback_query(
    F.data == "admin_users_all",
)
async def show_all_users(
    call: CallbackQuery,
    text: TextService,
):
    """Показывает всех пользователей."""

    async with SessionLocal() as session:
        user_service = UserService(session)
        users = await user_service.get_all()

    rich_message = build_users_text(
        users,
        text,
        "admin-users-all-title",
        count=len(users),
    )

    await call.message.edit_text(
        rich_message=rich_message,
        reply_markup=get_admin_users_kb(),
    )

    await call.answer()


@admin_users_router.callback_query(
    F.data == "admin_users_new_7",
)
async def show_new_users(
    call: CallbackQuery,
    text: TextService,
):
    """Показывает пользователей, зарегистрированных за последние 7 дней."""

    async with SessionLocal() as session:
        user_service = UserService(session)
        users = await user_service.get_new(7)

    rich_message = build_users_text(
        users,
        text,
        "admin-users-new-title",
        count=len(users),
    )

    await call.message.edit_text(
        rich_message=rich_message,
        reply_markup=get_admin_users_kb(),
    )

    await call.answer()