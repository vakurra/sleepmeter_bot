from typing import Literal

from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from constants.emoji import Emoji


ButtonStyle = Literal["primary", "success", "danger"] | None


def get_inline_keyboard(
    *,
    buttons: dict[str, tuple[str, ButtonStyle, Emoji | None]],
    sizes: tuple[int, ...] = (2,),
):
    """Создает inline-клавиатуру."""

    keyboard = InlineKeyboardBuilder()

    for text, (data, style, emoji) in buttons.items():
        kwargs = {
            "text": text,
            "style": style,
        }

        if data.startswith(("http://", "https://", "tg://")):
            kwargs["url"] = data
        else:
            kwargs["callback_data"] = data

        if emoji:
            kwargs["icon_custom_emoji_id"] = emoji.custom_id

        keyboard.add(InlineKeyboardButton(**kwargs))

    return keyboard.adjust(*sizes).as_markup()


def get_reply_keyboard(
    *,
    buttons: dict[str, tuple[ButtonStyle, Emoji | None]],
    placeholder: str | None = None,
    request_contact: int | None = None,
    request_location: int | None = None,
    sizes: tuple[int, ...] = (2,),
):
    """Создает reply-клавиатуру."""

    keyboard = ReplyKeyboardBuilder()

    for index, (text, (style, emoji)) in enumerate(buttons.items()):
        kwargs = {
            "text": text,
            "style": style,
        }

        if emoji:
            kwargs["icon_custom_emoji_id"] = emoji.custom_id

        if request_contact == index:
            kwargs["request_contact"] = True

        elif request_location == index:
            kwargs["request_location"] = True

        keyboard.add(KeyboardButton(**kwargs))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True,
        input_field_placeholder=placeholder,
    )
    