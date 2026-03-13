from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from personal_assistant.models.fields import Address, Birthday, Email, Name, Phone


@dataclass
class Record:
    name: Name
    phones: list[Phone] = field(default_factory=list)
    email: Email | None = None
    address: Address | None = None
    birthday: Birthday | None = None

    def __init__(self, name: str | Name):
        self.name = name if isinstance(name, Name) else Name(name)
        self.phones = []
        self.email = None
        self.address = None
        self.birthday = None

    def add_phone(self, phone: str) -> None:
        normalized = Phone(phone)
        if any(item.value == normalized.value for item in self.phones):
            raise ValueError("This phone already exists.")
        self.phones.append(normalized)

    def remove_phone(self, phone: str) -> None:
        for item in self.phones:
            if item.value == phone:
                self.phones.remove(item)
                return
        raise ValueError("Phone not found.")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        for index, item in enumerate(self.phones):
            if item.value == old_phone:
                self.phones[index] = Phone(new_phone)
                return
        raise ValueError("Old phone not found.")

    def set_email(self, email: str | None) -> None:
        self.email = Email(email) if email else None

    def set_address(self, address: str | None) -> None:
        self.address = Address(address) if address else None

    def set_birthday(self, birthday: str | None) -> None:
        self.birthday = Birthday(birthday) if birthday else None

    def matches(self, query: str) -> bool:
        query = query.lower().strip()
        haystacks = [self.name.value.lower()]
        haystacks.extend(phone.value.lower() for phone in self.phones)
        if self.email:
            haystacks.append(self.email.value.lower())
        if self.address:
            haystacks.append(self.address.value.lower())
        return any(query in item for item in haystacks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name.value,
            "phones": [phone.value for phone in self.phones],
            "email": self.email.value if self.email else None,
            "address": self.address.value if self.address else None,
            "birthday": self.birthday.value if self.birthday else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Record":
        record = cls(data["name"])
        for phone in data.get("phones", []):
            record.add_phone(phone)
        record.set_email(data.get("email"))
        record.set_address(data.get("address"))
        record.set_birthday(data.get("birthday"))
        return record

    def __str__(self) -> str:
        phones = ", ".join(phone.value for phone in self.phones) if self.phones else "-"
        email = self.email.value if self.email else "-"
        address = self.address.value if self.address else "-"
        birthday = self.birthday.value if self.birthday else "-"
        return (
            f"Name: {self.name.value} | Phones: {phones} | Email: {email} | "
            f"Address: {address} | Birthday: {birthday}"
        )
