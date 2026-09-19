from keyboards.builders import get_inline_keyboard
from constants import emoji


def get_admin_users_kb():
    """Кнопки выбора пользователей в админке."""

    return get_inline_keyboard(
        buttons={
            "Все пользователи": ("admin_users_all", None, emoji.USERS),
            "Новые за 7 дней": ("admin_users_new_7", None, None),
            "Назад": ("back_to_admin", "danger", emoji.BACK),
        },
        sizes=(1, 1, 1),
    )


def get_admin_users_pagination_kb(section: str, page: int, total_pages: int):
    """Кнопки пагинации списка пользователей."""

    buttons = {}

    if page > 1:
        buttons["←"] = (
            f"admin_users_page:{section}:{page - 1}",
            None,
            None,
        )

    buttons[f"{page} / {total_pages}"] = (
        "admin_users_page:noop:0",
        None,
        None,
    )

    if page < total_pages:
        buttons["→"] = (f"admin_users_page:{section}:{page + 1}", None, None)

    buttons["Назад"] = ("back_to_admin", "danger", emoji.BACK)

    return get_inline_keyboard(
        buttons=buttons,
        sizes=(3, 1),
    )