import json

import pytest

from personal_assistant.books.address_book import AddressBook
from personal_assistant.books.notes_book import NotesBook
from personal_assistant.models.note import Note
from personal_assistant.models.record import Record
from personal_assistant.storage.json_storage import JsonStorage


@pytest.fixture
def storage_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("PERSONAL_ASSISTANT_DATA_DIR", str(tmp_path))
    return tmp_path


class TestEnsureEnvironment:
    def test_creates_data_dir(self, storage_dir):
        JsonStorage.ensure_environment()
        assert storage_dir.exists()

    def test_creates_json_files(self, storage_dir):
        JsonStorage.ensure_environment()
        assert (storage_dir / "contacts.json").exists()
        assert (storage_dir / "notes.json").exists()

    def test_creates_history_file(self, storage_dir):
        JsonStorage.ensure_environment()
        assert (storage_dir / "history.txt").exists()

    def test_default_json_content(self, storage_dir):
        JsonStorage.ensure_environment()
        content = (storage_dir / "contacts.json").read_text(encoding="utf-8")
        assert content == "[]"

    def test_default_history_content(self, storage_dir):
        JsonStorage.ensure_environment()
        content = (storage_dir / "history.txt").read_text(encoding="utf-8")
        assert content == ""

    def test_does_not_overwrite_existing(self, storage_dir):
        (storage_dir / "contacts.json").write_text('[{"name": "test"}]', encoding="utf-8")
        JsonStorage.ensure_environment()
        content = (storage_dir / "contacts.json").read_text(encoding="utf-8")
        assert "test" in content


class TestLoadRaw:
    def test_load_empty_json(self, storage_dir):
        JsonStorage.ensure_environment()
        from personal_assistant.constants import get_contacts_file

        data = JsonStorage.load_raw(get_contacts_file())
        assert data == []

    def test_load_valid_data(self, storage_dir):
        from personal_assistant.constants import get_contacts_file

        path = get_contacts_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('[{"name": "Alice"}]', encoding="utf-8")
        data = JsonStorage.load_raw(path)
        assert len(data) == 1
        assert data[0]["name"] == "Alice"

    def test_load_corrupted_json(self, storage_dir):
        from personal_assistant.constants import get_contacts_file

        path = get_contacts_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{broken json!!!", encoding="utf-8")
        data = JsonStorage.load_raw(path)
        assert data == []

    def test_load_non_list_json(self, storage_dir):
        from personal_assistant.constants import get_contacts_file

        path = get_contacts_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"key": "value"}', encoding="utf-8")
        data = JsonStorage.load_raw(path)
        assert data == []


class TestSaveRaw:
    def test_save_creates_file(self, storage_dir):
        from personal_assistant.constants import get_contacts_file

        path = get_contacts_file()
        JsonStorage.save_raw(path, [{"name": "Test"}])
        assert path.exists()

    def test_save_writes_valid_json(self, storage_dir):
        from personal_assistant.constants import get_contacts_file

        path = get_contacts_file()
        JsonStorage.save_raw(path, [{"name": "Test"}])
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data == [{"name": "Test"}]

    def test_atomic_write_no_tmp_left(self, storage_dir):
        from personal_assistant.constants import get_contacts_file

        path = get_contacts_file()
        JsonStorage.save_raw(path, [{"name": "Test"}])
        assert not path.with_suffix(".tmp").exists()


class TestAddressBookRoundtrip:
    def test_save_and_load(self, storage_dir):
        book = AddressBook()
        record = Record("Maria")
        record.add_phone("0991112233")
        record.set_email("maria@test.com")
        book.add_record(record)

        JsonStorage.save_address_book(book)
        loaded = JsonStorage.load_address_book()

        assert loaded.find("Maria") is not None
        assert loaded.find("Maria").email.value == "maria@test.com"

    def test_load_empty_returns_empty_book(self, storage_dir):
        JsonStorage.ensure_environment()
        loaded = JsonStorage.load_address_book()
        assert len(loaded.all_records()) == 0

    def test_multiple_records(self, storage_dir):
        book = AddressBook()
        book.add_record(Record("Alice"))
        book.add_record(Record("Bob"))
        book.add_record(Record("Charlie"))

        JsonStorage.save_address_book(book)
        loaded = JsonStorage.load_address_book()
        assert len(loaded.all_records()) == 3


class TestNotesBookRoundtrip:
    def test_save_and_load(self, storage_dir):
        book = NotesBook()
        note = Note("Buy milk", ["home"])
        book.add_note(note)

        JsonStorage.save_notes_book(book)
        loaded = JsonStorage.load_notes_book()

        found = loaded.get_note_by_id(note.id)
        assert found is not None
        assert found.text == "Buy milk"

    def test_load_empty_returns_empty_book(self, storage_dir):
        JsonStorage.ensure_environment()
        loaded = JsonStorage.load_notes_book()
        assert len(loaded.all_notes()) == 0

    def test_preserves_tags(self, storage_dir):
        book = NotesBook()
        note = Note("Study", ["python", "coding"])
        book.add_note(note)

        JsonStorage.save_notes_book(book)
        loaded = JsonStorage.load_notes_book()

        found = loaded.get_note_by_id(note.id)
        tag_values = sorted(t.value for t in found.tags)
        assert tag_values == ["coding", "python"]
