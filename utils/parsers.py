import re
from datetime import time, datetime, date


def parse_time(text: str) -> time:
    """
    Преобразует строку формата ЧЧ:ММ в объект datetime.time.

    Допустимые форматы:
        23:30
        7:05
        07:05
    """

    text = text.strip()
    match = re.fullmatch(r"(\d{1,2}):(\d{2})", text)

    if not match:
        raise ValueError

    hour, minute = map(int, match.groups())

    if not (0 <= hour <= 23):
        raise ValueError

    if not (0 <= minute <= 59):
        raise ValueError

    return time(hour, minute)


def parse_duration(text: str) -> int:
    """
    Возвращает продолжительность сна в минутах.

    Допустимые форматы:
        7:30
        07:30
        7ч30м
        7 ч 30 м
        7 часов 30 минут
        7ч
        7 ч
        7 часов
    """

    text = text.lower().strip()
    match = re.fullmatch(r"(\d{1,2}):(\d{2})", text)  # Формат ЧЧ:ММ

    if match:
        hours, minutes = map(int, match.groups())

        if minutes >= 60:
            raise ValueError

        total_minutes = hours * 60 + minutes

        if not (60 <= total_minutes <= 16 * 60):
            raise ValueError

        return total_minutes

    # Формат "7ч30м", "7 ч 30 м", "7 часов 30 минут"
    match = re.fullmatch(r"(\d{1,2})\s*ч(?:ас(?:ов|а)?)?\s*(\d{1,2})?\s*(?:м(?:ин(?:ут(?:ы)?)?)?)?", text)

    if match:

        hours = int(match.group(1))
        minutes = int(match.group(2) or 0)

        if minutes >= 60:
            raise ValueError

        total_minutes = hours * 60 + minutes

        if not (60 <= total_minutes <= 16 * 60):
            raise ValueError

        return total_minutes

    raise ValueError


def parse_date(text: str) -> date:
    """
    Преобразует строку в дату.

    Допустимые форматы:
        05.07.2026
        05.07.26
    """

    text = text.strip()

    match = re.fullmatch(
        r"(\d{2})\.(\d{2})\.(\d{2}|\d{4})",
        text,
    )

    if not match:
        raise ValueError

    day, month, year = map(int, match.groups())

    if year < 100:
        year += 2000

    try:
        return date(year, month, day)

    except ValueError:
        raise ValueError