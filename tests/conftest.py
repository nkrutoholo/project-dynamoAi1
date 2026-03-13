import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

for path in (ROOT_DIR, SRC_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from personal_assistant.books.address_book import AddressBook
from personal_assistant.books.notes_book import NotesBook
from personal_assistant.models.note import Note
from personal_assistant.models.record import Record


@pytest.fixture
def record():
    r = Record("John Doe")
    r.add_phone("+380991112233")
    r.set_email("john@example.com")
    r.set_address("Kyiv, Main St 1")
    upcoming = date.today() + timedelta(days=3)
    r.set_birthday(upcoming.replace(year=upcoming.year - 30).strftime("%d.%m.%Y"))
    return r


@pytest.fixture
def address_book(record):
    book = AddressBook()
    book.add_record(record)

    r2 = Record("Jane Smith")
    r2.add_phone("0997776655")
    r2.set_email("jane@example.com")
    book.add_record(r2)

    r3 = Record("Bob Wilson")
    r3.add_phone("+380501234567")
    book.add_record(r3)

    return book


@pytest.fixture
def note():
    return Note("Buy groceries: milk, eggs, bread", ["shopping", "home"])


@pytest.fixture
def notes_book(note):
    book = NotesBook()
    book.add_note(note)

    n2 = Note("Learn Python decorators", ["study", "python"])
    book.add_note(n2)

    n3 = Note("Call dentist on Monday", ["health"])
    book.add_note(n3)

    return book
