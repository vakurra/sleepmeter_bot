from keyboards.builders import get_inline_keyboard
from constants import emoji


def get_settings_kb(notifications_enabled: bool):
    
    buttons = {
        "Изменить часовой пояс": ("settings_utc_offset", "success", emoji.EARTH),
        "Изменить время напоминания": ("settings_reminder_time", "success", emoji.CLOCK)
    }

    if notifications_enabled:
        buttons["Отключить уведомления"] = ("settings_notifications", "danger", emoji.BELL_OFF)
    else:
        buttons["Включить уведомления"] = ("settings_notifications", "success", emoji.BELL_ON)

    return get_inline_keyboard(buttons=buttons, sizes=(1, 1, 1))


def get_settings_utc_offset_kb():
    """Клавиатура изменения разницы с московским временем."""

    buttons = {}
    buttons["Назад"] = ("settings_back", "danger", emoji.BACK)
    buttons["Москва"] = (f"settings_msk_0", None, emoji.MOSCOW)

    for offset in range(-9, 10):
        if offset == 0:
            continue
        elif offset > 0:
            text = f"Мск +{offset}"
        else:
            text = f"Мск {offset}"

        buttons[text] = (f"settings_msk_{offset}", None, None)

    return get_inline_keyboard(buttons=buttons, sizes=(1, 1, 3,))


def get_settings_reminder_time_kb():
    """Клавиатура изменения времени напоминания."""

    buttons = {}

    hour = 4
    minute = 30

    buttons["Назад"] = ("settings_back", "danger", emoji.BACK)

    while (hour, minute) <= (16, 0):
        text = f"{hour:02}:{minute:02}"
        buttons[text] = (f"settings_time_{text}", None, None)
        minute += 30

        if minute == 60:
            minute = 0
            hour += 1

    return get_inline_keyboard(buttons=buttons, sizes=(1, 4,))