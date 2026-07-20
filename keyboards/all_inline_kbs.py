from keyboards.inline import get_inline_keyboard


# ================================
# Регистрация нового пользователя
# ================================
def get_utc_offset_kb(callback_prefix: str):
    """Клавиатура выбора разницы с московским временем."""

    buttons = {}

    for offset in range(-9, 10):
        if offset == 0:
            text = "🇷🇺 Москва"
        elif offset > 0:
            text = f"Мск +{offset}"
        else:
            text = f"Мск {offset}"

        buttons[text] = (
            f"{callback_prefix}_msk_{offset}",
            None,
        )

    return get_inline_keyboard(
        buttons=buttons,
        sizes=(3, 3, 3, 3, 3, 3, 1),
    )


def get_reminder_time_kb(callback_prefix: str):
    """Клавиатура выбора времени напоминания."""

    buttons = {}

    hour = 5
    minute = 0

    while (hour, minute) <= (16, 0):
        text = f"{hour:02}:{minute:02}"

        buttons[text] = (
            f"{callback_prefix}_time_{text}",
            None,
        )

        minute += 30

        if minute == 60:
            minute = 0
            hour += 1

    buttons["⬅️ Назад"] = (
        "reg_back",
        None,
    )

    return get_inline_keyboard(
        buttons=buttons,
        sizes=(4, 4, 4, 4, 4, 3, 1),
    )


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

        buttons[text] = (
            f"sleep_start_{text}",
            None,
        )

        if hour == 3 and minute == 30:
            break

        minute += 30

        if minute == 60:
            minute = 0
            hour += 1

            if hour == 24:
                hour = 0

    buttons["⌨️ Другое время"] = (
        "sleep_start_manual",
        "primary",
    )
    buttons["❌ Отмена"] = ("sleep_cancel", "danger")

    return get_inline_keyboard(
        buttons=buttons,
        sizes=(4, 4, 4, 4, 2),
    )

def get_cancel_record_kb():
    buttons = {}
    buttons["❌ Отмена"] = ("sleep_cancel", "danger")
    return get_inline_keyboard(
        buttons=buttons,
        sizes=(1,),
    )

def get_sleep_end_kb():
    """Клавиатура выбора времени пробуждения."""

    buttons = {}

    hour = 4
    minute = 0

    while True:
        text = f"{hour}:{minute:02}"

        buttons[text] = (
            f"sleep_end_{text}",
            None,
        )

        if hour == 13 and minute == 0:
            break

        minute += 30

        if minute == 60:
            minute = 0
            hour += 1

    buttons["⌨️ Другое"] = ("sleep_end_manual", "primary")
    buttons["⬅️ Назад"] = ("sleep_back", None)

    return get_inline_keyboard(
        buttons=buttons,
        sizes=(4, 4, 4, 4, 4, 4, 1),
    )


def get_sleep_rating_kb():
    """Клавиатура оценки качества сна."""

    buttons = {
        "⭐": ("sleep_rating_1", None),
        "⭐⭐": ("sleep_rating_2", None),
        "⭐⭐⭐": ("sleep_rating_3", None),
        "⭐⭐⭐⭐": ("sleep_rating_4", None),
        "⭐⭐⭐⭐⭐": ("sleep_rating_5", None),
        "⬅️ Назад": ("sleep_rating_back", None),
    }

    return get_inline_keyboard(
        buttons=buttons,
        sizes=(1, ),
    )


# ================================
# Настройки
# ================================
def get_settings_kb(notifications_enabled: bool):
    buttons = {
        "🌍 Изменить часовой пояс": ("settings_utc_offset", None),
        "⏰ Изменить время напоминания": ("settings_reminder_time", None),
        (
            "🔕 Отключить уведомления"
            if notifications_enabled
            else "🔔 Включить уведомления"
        ): ("settings_notifications", None),
    }

    return get_inline_keyboard(buttons=buttons, sizes=(1, 1, 1))


def get_settings_utc_offset_kb():
    """Клавиатура изменения разницы с московским временем."""

    buttons = {}

    for offset in range(-9, 10):
        if offset == 0:
            text = "🇷🇺 Москва"
        elif offset > 0:
            text = f"Мск +{offset}"
        else:
            text = f"Мск {offset}"

        buttons[text] = (f"settings_msk_{offset}", None)

    buttons["⬅️ Назад"] = ("settings_back", None)

    return get_inline_keyboard(
        buttons=buttons,
        sizes=(3, 3, 3, 3, 3, 3, 1),
    )


def get_settings_reminder_time_kb():
    """Клавиатура изменения времени напоминания."""

    buttons = {}

    hour = 5
    minute = 0

    while (hour, minute) <= (16, 0):
        text = f"{hour:02}:{minute:02}"
        buttons[text] = (f"settings_time_{text}", None)
        minute += 30

        if minute == 60:
            minute = 0
            hour += 1

    buttons["⬅️ Назад"] = ("settings_back", None)

    return get_inline_keyboard(
        buttons=buttons,
        sizes=(4, 4, 4, 4, 4, 3, 1),
    )


# ================================
# Обратная связь
# ================================
def get_feedback_kb():
    """Кнопки обратной связи."""

    return get_inline_keyboard(
        buttons={
            "⭐ Поддержать разработчика": ("support_dev", "primary"),
            "❌ Отмена": ("feedback_cancel", "danger"),
        },
        sizes=(1, 1),
    )

def get_support_options():
    """Кнопки с вариантами доната"""

    return get_inline_keyboard(
        buttons={
            "⭐ 1": ("support_amount:1", None),
            "⭐ 10": ("support_amount:10", None),
            "⭐ 50": ("support_amount:50", None),
            "⭐ 100": ("support_amount:100", None),
            "⬅️ Назад": ("support_back", None),
        },
        sizes=(4, 1),
    )