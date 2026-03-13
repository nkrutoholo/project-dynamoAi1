from __future__ import annotations

from personal_assistant.models.note import Note
from personal_assistant.utils.validators import validate_note_id


class NotesBook:
    def __init__(self):
        self._notes: list[Note] = []

    @property
    def notes(self) -> list[Note]:
        return self._notes

    def add_note(self, note: Note) -> None:
        if not isinstance(note, Note):
            raise TypeError("add_note expects Note instance.")

        if self.get_note_by_id(note.id) is not None:
            raise ValueError(f"Note with id {note.id} already exists.")

        self._notes.append(note)

    def get_note_by_id(self, note_id: int) -> Note | None:
        validated_id = validate_note_id(note_id)

        for note in self._notes:
            if note.id == validated_id:
                return note

        return None

    def delete_note(self, note_id: int) -> bool:
        note = self.get_note_by_id(note_id)

        if note is None:
            return False

        self._notes.remove(note)
        return True

    def all_notes(self) -> list[Note]:
        return list(self._notes)

    def find_notes(self, query: str) -> list[Note]:
        query = query.lower().strip()
        return [note for note in self._notes if query in note.text.lower()]

    def find_by_tag(self, tag: str) -> list[Note]:
        return [note for note in self._notes if note.has_tag(tag)]

    def to_list(self) -> list[dict]:
        return [note.to_dict() for note in self._notes]

    @classmethod
    def from_list(cls, items: list[dict]) -> NotesBook:
        book = cls()

        for item in items:
            note = Note.from_dict(item)
            book._notes.append(note)

        Note.sync_id_counter(book._notes)

        return book
