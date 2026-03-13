from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from personal_assistant.constants import get_contacts_file, get_data_dir, get_history_file, get_notes_file
from personal_assistant.books.address_book import AddressBook
from personal_assistant.books.notes_book import NotesBook


class JsonStorage:
    @staticmethod
    def ensure_environment() -> None:
        data_dir = get_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        for path in (get_contacts_file(), get_notes_file(), get_history_file()):
            if not path.exists():
                default = "[]" if path.suffix == ".json" else ""
                path.write_text(default, encoding="utf-8")

    @staticmethod
    def load_raw(path: Path) -> list[dict[str, Any]]:
        JsonStorage.ensure_environment()
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return []
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return []
        return data if isinstance(data, list) else []

    @staticmethod
    def save_raw(path: Path, items: list[dict[str, Any]]) -> None:
        JsonStorage.ensure_environment()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)

    @classmethod
    def load_address_book(cls) -> AddressBook:
        return AddressBook.from_list(cls.load_raw(get_contacts_file()))

    @classmethod
    def save_address_book(cls, book: AddressBook) -> None:
        cls.save_raw(get_contacts_file(), book.to_list())

    @classmethod
    def load_notes_book(cls) -> NotesBook:
        return NotesBook.from_list(cls.load_raw(get_notes_file()))

    @classmethod
    def save_notes_book(cls, book: NotesBook) -> None:
        cls.save_raw(get_notes_file(), book.to_list())
