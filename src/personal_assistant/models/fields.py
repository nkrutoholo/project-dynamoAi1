from __future__ import annotations

from personal_assistant.constants import DATE_FORMAT
from personal_assistant.utils.validators import (
    validate_address,
    validate_birthday,
    validate_email,
    validate_name,
    validate_phone,
)


class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    def __init__(self, value: str):
        self._value = ""
        super().__init__(value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        clean = value.strip()
        if not validate_name(clean):
            raise ValueError("Name cannot be empty.")
        self._value = clean


class Address(Field):
    def __init__(self, value: str):
        self._value = ""
        super().__init__(value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        clean = value.strip()
        if not validate_address(clean):
            raise ValueError("Address cannot be empty.")
        self._value = clean


class Phone(Field):
    def __init__(self, value: str):
        self._value = ""
        super().__init__(value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        clean = value.strip()
        if not validate_phone(clean):
            raise ValueError("Phone must be in format +380XXXXXXXXX or XXXXXXXXXX.")
        self._value = clean


class Email(Field):
    def __init__(self, value: str):
        self._value = ""
        super().__init__(value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        clean = value.strip()
        if not validate_email(clean):
            raise ValueError("Invalid email format.")
        self._value = clean


class Birthday(Field):
    def __init__(self, value: str):
        self._value = ""
        super().__init__(value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        clean = value.strip()
        if not validate_birthday(clean):
            raise ValueError(f"Birthday must be in format {DATE_FORMAT}.")
        self._value = clean
