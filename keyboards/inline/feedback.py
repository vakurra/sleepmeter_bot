from keyboards.builders import get_inline_keyboard
from constants import emoji


def get_feedback_kb():
    """Кнопки обратной связи."""

    return get_inline_keyboard(
        buttons={
            "Поддержать разработчика": ("support_dev", "primary", emoji.TGSTAR),
            "Отмена": ("feedback_cancel", "danger", emoji.CANCEL),
        },
        sizes=(1, 1),
    )

def get_support_options():
    """Кнопки с вариантами доната"""

    return get_inline_keyboard(
        buttons={
            "1": ("support_amount:1", None, emoji.ONE_TGSTAR),
            "10": ("support_amount:10", None, emoji.TWO_TGSTAR),
            "50": ("support_amount:50", None, emoji.THREE_TGSTAR),
            "100": ("support_amount:100", None, emoji.MEGA_TGSTAR),
            "Назад": ("support_back", "danger", emoji.BACK),
        },
        sizes=(4, 1),
    )


def get_feedback_answer_kb(user_id: int):
    """Кнопка ответа на обратную связь."""

    return get_inline_keyboard(
        buttons={
            "Ответить": (f"feedback_reply:{user_id}", "success", None),
        },
        sizes=(1,),
    )


def get_feedback_answer_cancel_kb():
    """Кнопка отмены ответа на обратную связь."""

    return get_inline_keyboard(
        buttons={
            "Отменить": ("feedback_reply_cancel", "danger", emoji.CANCEL),
        },
        sizes=(1,),
    )