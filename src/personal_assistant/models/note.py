from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Note:
    note_id: int
    text: str
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.text = self.text.strip()
        if not self.text:
            raise ValueError("Note text cannot be empty.")
        self.tags = self._normalize_tags(self.tags)

    @staticmethod
    def _normalize_tags(tags: list[str]) -> list[str]:
        normalized = []
        for tag in tags:
            clean = tag.strip().lower()
            if clean and clean not in normalized:
                normalized.append(clean)
        return normalized

    def add_tag(self, tag: str) -> None:
        clean = tag.strip().lower()
        if clean and clean not in self.tags:
            self.tags.append(clean)

    def remove_tag(self, tag: str) -> None:
        clean = tag.strip().lower()
        if clean not in self.tags:
            raise ValueError("Tag not found.")
        self.tags.remove(clean)

    def update_text(self, text: str) -> None:
        clean = text.strip()
        if not clean:
            raise ValueError("Note text cannot be empty.")
        self.text = clean

    def matches(self, query: str) -> bool:
        query = query.lower().strip()
        return query in self.text.lower() or any(query in tag for tag in self.tags)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.note_id, "text": self.text, "tags": self.tags}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Note":
        return cls(note_id=int(data["id"]), text=data["text"], tags=data.get("tags", []))

    def __str__(self) -> str:
        tags = ", ".join(self.tags) if self.tags else "-"
        return f"ID: {self.note_id} | Text: {self.text} | Tags: {tags}"
