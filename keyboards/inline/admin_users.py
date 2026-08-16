from keyboards.builders import get_inline_keyboard
from constants import emoji


def get_admin_users_kb():
    """Кнопки выбора пользователей в админке."""

    return get_inline_keyboard(
        buttons={
            "Все пользователи": (
                "admin_users_all",
                None,
                emoji.USERS,
            ),
            "Новые за 7 дней": (
                "admin_users_new_7",
                None,
                None,
            ),
            "Назад": (
                "back_to_admin",
                "danger",
                emoji.BACK,
            ),
        },
        sizes=(1, 1, 1),
    )