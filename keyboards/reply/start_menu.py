from keyboards.builders import get_reply_keyboard
from constants import emoji


start_reply_kb = get_reply_keyboard(
    buttons={
        "Сделать запись за сегодня": ("success", emoji.MOON),
        "Изменить/добавить запись": (None, emoji.UPDATE),
        "Статистика за 7 дней": (None, emoji.STATISTICS),
        "Статистика за месяц": (None, emoji.STATISTICS),
        "Настройки": ("primary", emoji.SETTINGS),
        "Обратная связь": ("primary", emoji.FEEDBACK),
    },
    placeholder="Выбери кнопку",
    sizes=(1, 1, 2, 2),
)