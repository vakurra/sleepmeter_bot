import re
from pathlib import Path
from typing import Any

from fluent.runtime import FluentLocalization, FluentResourceLoader
from aiogram.types import (
    InputRichBlockSectionHeading,
    InputRichBlockTable,
    InputRichBlockParagraph,
    RichBlockTableCell,
    RichTextBold,
    RichTextCode,
    RichTextCustomEmoji,
    RichTextItalic,
    RichTextStrikethrough,
    RichTextUnderline,
)

from constants import emoji


class TextService:
    def __init__(self, locale: str = "ru") -> None:
        locales = Path(__file__).resolve().parents[2] / "locales"
        loader = FluentResourceLoader(str(locales))

        self._fluent = FluentLocalization(
            locales=[locale],
            resource_ids=[f"{locale}.ftl"],
            resource_loader=loader,
        )

        self._emoji = {
            name.lower(): value
            for name, value in vars(emoji).items()
            if isinstance(value, emoji.Emoji)
        }

    def __call__(self, key: str, **kwargs) -> str:
        """Обычный текст с HTML emoji."""

        variables = {
            **kwargs,
            **{
                name: value.html()
                for name, value in self._emoji.items()
            },
        }

        return self._fluent.format_value(key, variables)

    def rich_text(self, value: str):
        """
        Преобразует строку в список Telegram RichText.

        Поддерживаемое форматирование:

            **жирный**
            *курсив*
            __подчеркнутый__
            ~~зачеркнутый~~
            `код`
            [текст](https://example.com)

        Также поддерживаются custom emoji вида:

            __EMOJI_BONUS__

        Вложенное форматирование поддерживается.
        """

        patterns = (
            ("**", RichTextBold),
            ("__", RichTextUnderline),
            ("~~", RichTextStrikethrough),
            ("*", RichTextItalic),
            ("```", RichTextCode),
        )

        result = []
        buffer = []
        index = 0

        def flush_buffer():
            if buffer:
                result.append("".join(buffer))
                buffer.clear()

        while index < len(value):
            # Custom emoji
            if value.startswith("__EMOJI_", index):
                end = value.find("__", index + 8)

                if end != -1:
                    name = value[index + 8:end]

                    if name in self._emoji:
                        flush_buffer()
                        result.append(self._emoji[name].rich())
                        index = end + 2
                        continue
            
            # Форматирование
            matched = False

            for marker, rich_type in patterns:
                if not value.startswith(marker, index):
                    continue

                end = value.find(marker, index + len(marker))

                if end == -1 or end == index + len(marker):
                    continue

                flush_buffer()

                inner = self.rich_text(
                    value[index + len(marker):end]
                )

                result.append(
                    rich_type(text=inner)
                )

                index = end + len(marker)
                matched = True
                break

            if matched:
                continue

            buffer.append(value[index])
            index += 1

        flush_buffer()

        return result

    def rich(self, key: str, **kwargs):
        variables = {
            **kwargs,
            **{
                name: f"__EMOJI_{name}__"
                for name in self._emoji
            },
        }

        raw = self._fluent.format_value(key, variables)

        return self.rich_text(raw)
    
    def table(
        self,
        key: str,
        *,
        header: bool | None = True,
        bordered: bool | None = True,
        striped: bool | None = False,
        **kwargs: Any,
    ) -> InputRichBlockTable:
        """
        Создает Telegram Rich Table по описанию из .ftl-файла.

        Таблица описывается построчно. Ячейки одной строки
        разделяются символом "|". Количество строк и столбцов не ограничено,
        все строки должны содержать одинаковое количество ячеек.

        В ячейках поддерживаются:
        - переменные Fluent;
        - custom emoji из constants.emoji;
        - обычный текст.

        Первая строка может быть автоматически оформлена как заголовок
        с помощью параметра ``header=True``.

        Args:
            key: Ключ из .ftl-файла.
            header: Если True, первая строка таблицы будет заголовком.
            bordered: Отображать границы таблицы, если True.
            striped: Использовать чередование фона строк, если True.
            **kwargs: Переменные Fluent.

        Returns:
            Готовый InputRichBlockTable для использования в InputRichMessage.

        Raises:
            ValueError: Если ресурс пустой, не содержит столбцов или строки
                имеют разное количество ячеек.

        Example:
            В locales/ru.ftl:

                profile-table =
                    Параметр | Значение
                    Имя | { $name }
                    Username | { $username }
                    Бонусы | { $bonus } { $balance }
                    Регистрация | { $created_at }

            В handler:

                table = text.table(
                    "profile-table",
                    header=False,
                    bordered=True,
                    striped=True,
                    name=user.first_name,
                    username=username,
                    balance=user.balance,
                    created_at=user.created_at.strftime("%d.%m.%Y"),
                )
        """

        variables = {
            **kwargs,
            **{
                name: f"__EMOJI_{name}__"
                for name in self._emoji
            },
        }

        raw = self._fluent.format_value(key, variables)
        rows = []

        for line in raw.splitlines():
            line = line.strip()

            if not line:
                continue

            cells = [cell.strip() for cell in line.split("|")]
            rows.append(cells)

        if not rows:
            raise ValueError(f"Table resource '{key}' is empty")

        column_count = len(rows[0])

        if column_count == 0:
            raise ValueError(f"Table resource '{key}' has no columns")

        for index, row in enumerate(rows, start=1):
            if len(row) != column_count:
                raise ValueError(
                    f"Table resource '{key}' has invalid row "
                    f"{index}: expected {column_count} columns, "
                    f"got {len(row)}"
                )

        cells = [
            [
                RichBlockTableCell(
                    align="left",
                    valign="middle",
                    text=self.rich_text(cell),
                    is_header=header and row_index == 0,
                )
                for cell in row
            ]
            for row_index, row in enumerate(rows)
        ]

        return InputRichBlockTable(
            cells=cells,
            is_bordered=bordered,
            is_striped=striped,
        )

    def heading(
        self,
        key: str,
        *,
        size: int = 1,
        **kwargs: Any,
    ) -> InputRichBlockSectionHeading:
        """Создает заголовок Telegram Rich Message по .ftl-ключу.

        Args:
            key: Ключ локализованного ресурса.
            size: Размер заголовка от 1 до 6.
            **kwargs: Переменные Fluent.
        """

        if not 1 <= size <= 6:
            raise ValueError(f"Heading size must be between 1 and 6, got {size}")

        return InputRichBlockSectionHeading(
            text=self.rich(key, **kwargs),
            size=size,
        )

    def paragraph(
        self,
        key: str,
        **kwargs: Any,
    ) -> InputRichBlockParagraph:
        """Создает текстовый блок Rich Message."""

        return InputRichBlockParagraph(
            text=self.rich(key, **kwargs),
        )