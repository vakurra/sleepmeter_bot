from typing import Literal
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

ButtonStyle = Literal["primary", "success", "danger"] | None

def get_inline_keyboard(
    *,
    buttons: dict[str, tuple[str, ButtonStyle]],
    sizes: tuple[int, ...] = (2,),
):
    """Создает inline-клавиатуру."""

    keyboard = InlineKeyboardBuilder()

    for text, (data, style) in buttons.items():
        keyboard.add(
            InlineKeyboardButton(
                text=text,
                callback_data=data,
                style=style,
            )
        )

    return keyboard.adjust(*sizes).as_markup()

