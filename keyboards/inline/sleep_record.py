from keyboards.builders import get_inline_keyboard
from constants import emoji


# ================================
# Новая запись о сне
# ================================
def get_sleep_start_kb():
    """Клавиатура выбора времени отхода ко сну."""

    buttons = {}

    hour = 20
    minute = 0

    while True:
        text = f"{hour:02}:{minute:02}"
        buttons[text] = (f"sleep_start_{text}", None, None)

        if hour == 5 and minute == 0:
            break

        minute += 30

        if minute == 60:
            minute = 0
            hour += 1

            if hour == 24:
                hour = 0

    buttons["Другое"] = ("sleep_start_manual", "primary", emoji.INPUT)
    buttons["Отмена"] = ("sleep_cancel", "danger", emoji.CANCEL)

    return get_inline_keyboard(buttons=buttons, sizes=(4,))

def get_cancel_record_kb():
    buttons = {}
    buttons["Отмена"] = ("sleep_cancel", "danger", emoji.CANCEL)

    return get_inline_keyboard(buttons=buttons, sizes=(1,))

def get_sleep_end_kb():
    """Клавиатура выбора времени пробуждения."""

    buttons = {}

    hour = 4
    minute = 0

    while True:
        text = f"{hour}:{minute:02}"

        buttons[text] = (f"sleep_end_{text}", None, None)

        if hour == 13 and minute == 0:
            break

        minute += 30

        if minute == 60:
            minute = 0
            hour += 1

    buttons["Другое"] = ("sleep_end_manual", "primary", emoji.INPUT)
    buttons["Назад"] = ("sleep_back", "danger", emoji.BACK)

    return get_inline_keyboard(buttons=buttons, sizes=(4,))


def get_sleep_rating_kb():
    """Клавиатура оценки качества сна."""

    buttons = {
        "⭐": ("sleep_rating_1", None, None),
        "⭐⭐": ("sleep_rating_2", None, None),
        "⭐⭐⭐": ("sleep_rating_3", None, None),
        "⭐⭐⭐⭐": ("sleep_rating_4", None, None),
        "⭐⭐⭐⭐⭐": ("sleep_rating_5", None, None),
        "Назад": ("sleep_rating_back", "danger", emoji.BACK),
    }

    return get_inline_keyboard(buttons=buttons, sizes=(1, ))
