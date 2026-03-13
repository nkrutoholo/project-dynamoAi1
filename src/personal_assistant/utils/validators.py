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
    try:
        datetime.strptime(date_str.strip(), DATE_FORMAT)
        return True
    except ValueError:
        return False
