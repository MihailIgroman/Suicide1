"""Шар даних. Жодних імпортів з PySide6."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Note:
    id: int
    text: str = ""
    pinned: bool = False
    updated_at: str = ""

    def touch(self):
        """Запам'ятати час останньої зміни."""
        self.updated_at = datetime.now().isoformat(sep=" ", timespec="seconds")

    def preview(self, length):
        """Перший рядок тексту, обрізаний до length символів."""
        first_line = self.text.strip().split("\n", 1)[0].strip()
        if not first_line:
            return "(empty)"
        if len(first_line) <= length:
            return first_line
        return first_line[:length].rstrip() + "..."

    def is_long(self, limit):
        return len(self.text) >= limit

    @staticmethod
    def from_row(row):
        """Створює нотатку з рядка БД. Кидає ValueError на некоректних даних."""
        if len(row) != 4:
            raise ValueError(f"Expected 4 columns, got {len(row)}")

        note_id, text, pinned, updated_at = row

        if not isinstance(note_id, int):
            raise ValueError(f"Bad note id: {note_id!r}")
        if not isinstance(text, str):
            raise ValueError(f"Bad note text in note {note_id}")

        return Note(
            id=note_id,
            text=text,
            pinned=bool(pinned),
            updated_at=str(updated_at or ""),
        )

    def to_row(self):
        return (self.id, self.text, int(self.pinned), self.updated_at)
