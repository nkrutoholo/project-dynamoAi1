import pytest

from personal_assistant.books.notes_book import NotesBook
from personal_assistant.models.note import Note


class TestNotesBookCRUD:
    def test_add_and_get(self, notes_book, note):
        found = notes_book.get_note_by_id(note.id)
        assert found is not None
        assert found.text == note.text

    def test_get_nonexistent(self, notes_book):
        assert notes_book.get_note_by_id(9999) is None

    def test_delete_existing(self, notes_book, note):
        assert notes_book.delete_note(note.id) is True
        assert notes_book.get_note_by_id(note.id) is None

    def test_delete_nonexistent(self, notes_book):
        assert notes_book.delete_note(9999) is False

    def test_all_notes_returns_all(self, notes_book):
        assert len(notes_book.all_notes()) == 3

    def test_add_duplicate_id_raises(self, notes_book, note):
        with pytest.raises(ValueError):
            notes_book.add_note(note)


class TestNotesBookSearch:
    def test_find_by_text(self, notes_book):
        results = notes_book.find_notes("Python")
        assert len(results) == 1

    def test_find_case_insensitive(self, notes_book):
        results = notes_book.find_notes("python")
        assert len(results) == 1

    def test_find_no_results(self, notes_book):
        assert len(notes_book.find_notes("zzzzzzz")) == 0

    def test_find_by_tag(self, notes_book):
        results = notes_book.find_by_tag("shopping")
        assert len(results) == 1

    def test_find_by_tag_no_results(self, notes_book):
        assert len(notes_book.find_by_tag("nonexistent")) == 0


class TestNoteTagsCRUD:
    def test_add_tag(self, note):
        note.add_tag("urgent")
        assert note.has_tag("urgent")

    def test_add_duplicate_tag_ignored(self, note):
        count_before = len(note.tags)
        note.add_tag("shopping")
        assert len(note.tags) == count_before

    def test_delete_tag(self, note):
        assert note.delete_tag("shopping") is True
        assert not note.has_tag("shopping")

    def test_delete_nonexistent_tag(self, note):
        assert note.delete_tag("nonexistent") is False

    def test_change_tag(self, note):
        assert note.change_tag("shopping", "groceries") is True
        assert note.has_tag("groceries")
        assert not note.has_tag("shopping")

    def test_change_nonexistent_tag(self, note):
        assert note.change_tag("nonexistent", "new") is False

    def test_has_tag_case_insensitive(self, note):
        assert note.has_tag("Shopping")


class TestNotesBookSerialization:
    def test_roundtrip(self, notes_book):
        data = notes_book.to_list()
        restored = NotesBook.from_list(data)
        assert len(restored.all_notes()) == len(notes_book.all_notes())

    def test_roundtrip_preserves_tags(self, notes_book, note):
        data = notes_book.to_list()
        restored = NotesBook.from_list(data)
        found = restored.get_note_by_id(note.id)
        assert found is not None
        original_tags = sorted(t.value for t in note.tags)
        restored_tags = sorted(t.value for t in found.tags)
        assert original_tags == restored_tags

    def test_from_empty_list(self):
        book = NotesBook.from_list([])
        assert len(book.all_notes()) == 0


class TestSortByTags:
    def test_sort_notes_by_tags(self):
        book = NotesBook()
        book.add_note(Note("Z note", ["zeta"]))
        book.add_note(Note("A note", ["alpha"]))
        book.add_note(Note("M note", ["middle"]))

        sorted_notes = sorted(
            book.all_notes(),
            key=lambda n: (
                tuple(t.value for t in sorted(n.tags, key=lambda t: t.value)),
                n.id,
            ),
        )
        tags_order = [sorted_notes[i].tags[0].value for i in range(3)]
        assert tags_order == ["alpha", "middle", "zeta"]
