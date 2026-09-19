from aiogram import F, Router
from aiogram.types import CallbackQuery, InputRichMessage, Message

from database.session import SessionLocal
from keyboards.inline.admin_users import get_admin_users_kb, get_admin_users_pagination_kb
from middlewares.admin import AdminMiddleware
from services.bot.text import TextService
from services.db.user import UserService


USERS_PER_PAGE = 25

admin_users_router = Router()

admin_users_router.message.middleware(AdminMiddleware())
admin_users_router.callback_query.middleware(AdminMiddleware())


def paginate_users(users, page: int):
    total = len(users)
    total_pages = max(
        1,
        (total + USERS_PER_PAGE - 1) // USERS_PER_PAGE,
    )

    page = max(1, min(page, total_pages))

    start = (page - 1) * USERS_PER_PAGE
    end = start + USERS_PER_PAGE

    return (
        users[start:end],
        page,
        total_pages,
        total,
    )


def escape_table_value(value: str) -> str:
    """Экранирует символы, используемые как разделители таблицы."""

    return value.replace("|", "¦")


def build_users_text(
    users,
    text: TextService,
    title_key: str,
    **kwargs,
) -> InputRichMessage:
    """Формирует Rich Message со списком пользователей."""

    rows = [
        f"{escape_table_value(user.first_name or 'Без имени')} | "
        f"@{escape_table_value(user.username or 'нет')} | "
        f"{user.created_at:%d.%m.%Y} | "
        f"{escape_table_value(user.referred_by or '—')} | "
        f"{sleep_records_count} | "
        f"{'✅' if user.notifications_enabled else '❌'}"
        for user, sleep_records_count in users
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


def build_new_users_text(
    users,
    text: TextService,
    title_key: str,
    **kwargs,
) -> InputRichMessage:
    """Формирует Rich Message со списком новых пользователей."""

    rows = [
        f"{escape_table_value(user.first_name or 'Без имени')} | "
        f"@{escape_table_value(user.username or 'нет')} | "
        f"{user.created_at:%d.%m.%Y} | "
        f"{escape_table_value(user.referred_by or '—')}"
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
                "admin-users-new-table",
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


@admin_users_router.callback_query(F.data == "admin_users_all")
async def show_all_users(call: CallbackQuery, text: TextService):
    """Показывает первую страницу всех пользователей."""

    async with SessionLocal() as session:
        user_service = UserService(session)
        users = await user_service.get_all_with_stats()

    page_users, page, total_pages, total = paginate_users(users, 1)

    rich_message = build_users_text(
        page_users,
        text,
        "admin-users-all-title",
        count=total,
    )

    await call.message.edit_text(
        rich_message=rich_message,
        reply_markup=get_admin_users_pagination_kb(
            section="all",
            page=page,
            total_pages=total_pages,
        ),
    )

    await call.answer()


@admin_users_router.callback_query(F.data == "admin_users_new_7")
async def show_new_users(call: CallbackQuery, text: TextService):
    """Показывает первую страницу новых пользователей."""

    async with SessionLocal() as session:
        user_service = UserService(session)
        users = await user_service.get_new(7)

    page_users, page, total_pages, total = paginate_users(users, 1)

    rich_message = build_new_users_text(
        page_users,
        text,
        "admin-users-new-title",
        count=total,
    )

    await call.message.edit_text(
        rich_message=rich_message,
        reply_markup=get_admin_users_pagination_kb(
            section="new",
            page=page,
            total_pages=total_pages,
        ),
    )

    await call.answer()


@admin_users_router.callback_query(F.data.startswith("admin_users_page:"))
async def show_users_page(call: CallbackQuery,text: TextService):
    
    _, section, page_raw = call.data.split(":", 2)

    if section == "noop":
        await call.answer()
        return

    page = int(page_raw)

    async with SessionLocal() as session:
        user_service = UserService(session)

        if section == "all":
            users = await user_service.get_all_with_stats()
            build_text = build_users_text
            title_key = "admin-users-all-title"

        elif section == "new":
            users = await user_service.get_new(7)
            build_text = build_new_users_text
            title_key = "admin-users-new-title"

        else:
            await call.answer()
            return

    page_users, page, total_pages, total = paginate_users(users, page)

    rich_message = build_text(
        page_users,
        text,
        title_key,
        count=total,
    )

    await call.message.edit_text(
        rich_message=rich_message,
        reply_markup=get_admin_users_pagination_kb(
            section=section,
            page=page,
            total_pages=total_pages,
        ),
    )

    await call.answer()
