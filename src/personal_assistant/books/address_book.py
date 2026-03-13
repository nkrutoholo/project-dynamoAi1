from __future__ import annotations

from collections import UserDict
from collections.abc import Iterable
from datetime import date, datetime

from personal_assistant.constants import DATE_FORMAT
from personal_assistant.models.record import Record


class AddressBook(UserDict):
    def add_record(self, record: Record) -> None:
        key = record.name.value.lower()
        if key in self.data:
            raise ValueError("Contact with this name already exists.")
        self.data[key] = record

    def find(self, name: str) -> Record | None:
        return self.data.get(name.strip().lower())

    def delete(self, name: str) -> None:
        key = name.strip().lower()
        if key not in self.data:
            raise KeyError("Contact not found.")
        del self.data[key]

    def search(self, query: str) -> list[Record]:
        return [record for record in self.data.values() if record.matches(query)]

    def all_records(self) -> list[Record]:
        return sorted(self.data.values(), key=lambda item: item.name.value.lower())

    def get_upcoming_birthdays(self, days: int) -> list[Record]:
        if days < 0:
            raise ValueError("Days must be a non-negative integer.")
        today = date.today()
        upcoming: list[Record] = []
        for record in self.data.values():
            if not record.birthday:
                continue
            birthday = datetime.strptime(record.birthday.value, DATE_FORMAT).date()
            nearest = birthday.replace(year=today.year)
            if nearest < today:
                nearest = nearest.replace(year=today.year + 1)
            delta = (nearest - today).days
            if 0 <= delta <= days:
                upcoming.append(record)
        return sorted(
            upcoming,
            key=lambda item: datetime.strptime(item.birthday.value, DATE_FORMAT).month if item.birthday else 13,
        )

    def to_list(self) -> list[dict]:
        return [record.to_dict() for record in self.all_records()]

    @classmethod
    def from_list(cls, items: Iterable[dict]) -> AddressBook:
        book = cls()
        for item in items:
            book.add_record(Record.from_dict(item))
        return book
