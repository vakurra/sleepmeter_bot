from typing import Dict, Tuple
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_keyboard(
    *,
    buttons: Dict[str, str],
    sizes: Tuple[int] = (2,)
):

    keyboard = InlineKeyboardBuilder()

    for text, data in buttons.items(): 
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()
