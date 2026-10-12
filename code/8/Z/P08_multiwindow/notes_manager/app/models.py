# Шар даних. Жодних імпортів з PySide6.

from dataclasses import dataclass
from datetime import datetime

TIME_FORMAT = "%Y-%m-%d %H:%M"      # той самий формат, що й у практичних 3-5


def now_text():
    return datetime.now().strftime(TIME_FORMAT)


@dataclass
class Note:
    id: int
    text: str = ""
    created_at: str = ""
    updated_at: str = ""
    pinned: bool = False

    def touch(self):
        # Запам'ятати час останньої зміни.
        self.updated_at = now_text()

    def preview(self, length):
        # Перший рядок тексту, обрізаний до length символів.
        first_line = self.text.strip().split("\n", 1)[0].strip()
        if not first_line:
            return "(empty)"
        if len(first_line) <= length:
            return first_line
        return first_line[:length].rstrip() + "..."

    def to_row(self):
        return (self.id, self.text, self.created_at, self.updated_at, int(self.pinned))

    @staticmethod
    def from_row(row):
        # Створює нотатку з рядка БД. Кидає ValueError на некоректних даних.
        if len(row) != 5:
            raise ValueError(f"Expected 5 columns, got {len(row)}")

        note_id, text, created_at, updated_at, pinned = row

        if not isinstance(note_id, int):
            raise ValueError(f"Bad note id: {note_id!r}")
        if not isinstance(text, str):
            raise ValueError(f"Bad note text in note {note_id}")

        return Note(
            id=note_id,
            text=text,
            created_at=str(created_at or ""),
            updated_at=str(updated_at or created_at or ""),
            pinned=bool(pinned),
        )
