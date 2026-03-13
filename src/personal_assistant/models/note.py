from __future__ import annotations

from personal_assistant.models.fields import Tag
from personal_assistant.utils.validators import (
    validate_note_id,
    validate_note_text,
    validate_tags_list,
)


class Note:
    _id_counter: int = 1

    def __init__(self, text: str, tags: list[str] | None = None):
        self._id = self._generate_id()
        self._text = ""
        self._tags: list[Tag] = []

        self.text = text

        for tag in validate_tags_list(tags):
            self.add_tag(tag)

    @classmethod
    def _generate_id(cls) -> int:
        current_id = cls._id_counter
        cls._id_counter += 1
        return current_id

    @property
    def id(self) -> int:
        return self._id

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = validate_note_text(value)

    @property
    def tags(self) -> list[Tag]:
        return self._tags

    def add_tag(self, tag: str) -> None:
        new_tag = Tag(tag)

        if not self.has_tag(new_tag.value):
            self._tags.append(new_tag)

    def change_tag(self, old_tag: str, new_tag: str) -> bool:
        old_normalized = Tag(old_tag).value
        new_normalized = Tag(new_tag).value

        for index, existing in enumerate(self._tags):
            if existing.value == old_normalized:
                if self.has_tag(new_normalized):
                    self._tags.pop(index)
                else:
                    self._tags[index] = Tag(new_normalized)
                return True

        return False

    def has_tag(self, tag: str) -> bool:
        normalized = Tag(tag).value
        return any(existing.value == normalized for existing in self._tags)

    def delete_tag(self, tag: str) -> bool:
        normalized = Tag(tag).value

        for existing in self._tags:
            if existing.value == normalized:
                self._tags.remove(existing)
                return True

        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "tags": [tag.value for tag in self.tags],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        if not isinstance(data, dict):
            raise ValueError("Note data must be a dictionary.")

        raw_id = data.get("id")
        raw_text = data.get("text", "")
        raw_tags = data.get("tags", [])

        note = cls(text=raw_text, tags=raw_tags)

        if raw_id is not None:
            validated_id = validate_note_id(raw_id)
            note._id = validated_id

            if validated_id >= cls._id_counter:
                cls._id_counter = validated_id + 1

        return note

    @classmethod
    def sync_id_counter(cls, notes: list["Note"]) -> None:
        if not notes:
            cls._id_counter = 1
            return

        max_id = max(note.id for note in notes)
        cls._id_counter = max_id + 1

    def __str__(self) -> str:
        tags_str = ", ".join(tag.value for tag in self.tags) if self.tags else "-"
        return f"ID: {self.id} | Text: {self.text} | Tags: {tags_str}"