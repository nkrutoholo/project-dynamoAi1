import pytest

from personal_assistant.books.address_book import AddressBook
from personal_assistant.models.record import Record


class TestAddressBookCRUD:
    def test_find_existing(self, address_book):
        assert address_book.find("John Doe") is not None

    def test_find_case_insensitive(self, address_book):
        assert address_book.find("john doe") is not None

    def test_find_nonexistent(self, address_book):
        assert address_book.find("Nobody") is None

    def test_add_duplicate_raises(self, address_book, record):
        with pytest.raises(ValueError):
            address_book.add_record(record)

    def test_delete_existing(self, address_book):
        address_book.delete("Jane Smith")
        assert address_book.find("Jane Smith") is None

    def test_delete_nonexistent_raises(self, address_book):
        with pytest.raises(KeyError):
            address_book.delete("Nobody")

    def test_all_records_sorted(self, address_book):
        records = address_book.all_records()
        names = [r.name.value for r in records]
        assert names == sorted(names, key=str.lower)


class TestAddressBookSearch:
    def test_search_by_name(self, address_book):
        results = address_book.search("John")
        assert len(results) == 1
        assert results[0].name.value == "John Doe"

    def test_search_by_phone(self, address_book):
        results = address_book.search("+380991112233")
        assert len(results) == 1

    def test_search_by_email(self, address_book):
        results = address_book.search("jane@example")
        assert len(results) == 1

    def test_search_no_results(self, address_book):
        assert len(address_book.search("zzzzzzz")) == 0

    def test_search_partial_match(self, address_book):
        results = address_book.search("example.com")
        assert len(results) == 2


class TestAddressBookBirthdays:
    def test_upcoming_birthdays(self, address_book):
        results = address_book.get_upcoming_birthdays(5)
        assert len(results) == 1
        assert results[0].name.value == "John Doe"

    def test_no_upcoming_birthdays(self, address_book):
        results = address_book.get_upcoming_birthdays(0)
        assert len(results) == 0

    def test_negative_days_raises(self, address_book):
        with pytest.raises(ValueError):
            address_book.get_upcoming_birthdays(-1)


class TestAddressBookSerialization:
    def test_roundtrip(self, address_book):
        data = address_book.to_list()
        restored = AddressBook.from_list(data)
        assert len(restored.all_records()) == len(address_book.all_records())
        assert restored.find("John Doe") is not None
        assert restored.find("John Doe").email.value == "john@example.com"
