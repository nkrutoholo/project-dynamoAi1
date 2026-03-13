from __future__ import annotations

import re
from datetime import datetime

from personal_assistant.constants import DATE_FORMAT


def validate_name(name: str) -> bool:
    return bool(name and name.strip())


def validate_address(address: str) -> bool:
    return bool(address and address.strip())


def validate_phone(phone: str) -> bool:
    pattern = r"^(\+380\d{9}|0\d{9})$"
    return bool(re.fullmatch(pattern, phone.strip()))


def validate_email(email: str) -> bool:
    pattern = r"^[\w.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
    return bool(re.fullmatch(pattern, email.strip()))


def validate_birthday(date_str: str) -> bool:
    """Birthday must be in DD.MM.YYYY format and not in the future."""
    try:
        dt = datetime.strptime(date_str.strip(), DATE_FORMAT).date()
        return dt <= datetime.now().date()
    except ValueError:
        return False


def validate_note_text(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Note text must be a string.")

    normalized = value.strip()

    if not normalized:
        raise ValueError("Note text can't be empty.")

    if len(normalized) > 500:
        raise ValueError("Note text is too long. Maximum length is 500 characters.")

    return normalized


def validate_tag(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Tag must be a string.")

    normalized = value.strip().lower()

    if not normalized:
        raise ValueError("Tag can't be empty.")

    if len(normalized) > 30:
        raise ValueError("Tag is too long. Maximum length is 30 characters.")

    if not re.fullmatch(r"[a-zA-Zа-яА-ЯіїєґІЇЄҐ0-9_-]+", normalized):  # noqa: RUF001
        raise ValueError("Tag may contain only letters, digits, underscore and hyphen.")

    return normalized


def validate_note_id(value: str | int) -> int:
    if isinstance(value, int):
        note_id = value
    elif isinstance(value, str):
        value = value.strip()
        if not value:
            raise ValueError("Note ID can't be empty.")
        try:
            note_id = int(value)
        except ValueError:
            raise ValueError("Note ID must be a number.")
    else:
        raise ValueError("Note ID must be a number.")

    if note_id <= 0:
        raise ValueError("Note ID must be greater than zero.")

    return note_id


def validate_tags_list(tags: list[str] | None) -> list[str]:
    if tags is None:
        return []

    if not isinstance(tags, list):
        raise ValueError("Tags must be provided as a list.")

    normalized_tags: list[str] = []
    seen: set[str] = set()

    for tag in tags:
        normalized = validate_tag(tag)
        if normalized not in seen:
            normalized_tags.append(normalized)
            seen.add(normalized)

    return normalized_tags
