from keyboards.builders import get_inline_keyboard
from constants import emoji


def get_utc_offset_kb(callback_prefix: str):
    """Клавиатура выбора разницы с московским временем."""

    buttons = {}
    buttons["Москва"] = (f"{callback_prefix}_msk_0", None, emoji.MOSCOW)

    for offset in range(-9, 10):
        if offset == 0:
            continue
        elif offset > 0:
            text = f"Мск +{offset}"
        else:
            text = f"Мск {offset}"

        buttons[text] = (f"{callback_prefix}_msk_{offset}", None, None)

    return get_inline_keyboard(buttons=buttons, sizes=(1, 3,))


def get_reminder_time_kb(callback_prefix: str):
    """Клавиатура выбора времени напоминания."""

    buttons = {}

    hour = 4
    minute = 30

    buttons["Назад"] = ("reg_back", "danger", emoji.BACK)

    while (hour, minute) <= (16, 0):
        text = f"{hour:02}:{minute:02}"
        buttons[text] = (f"{callback_prefix}_time_{text}", None, None)
        minute += 30

        if minute == 60:
            minute = 0
            hour += 1

    return get_inline_keyboard(buttons=buttons, sizes=(1, 4,))
