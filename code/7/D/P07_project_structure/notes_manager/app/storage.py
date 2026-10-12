# Шар збереження. Знає про моделі, базу SQLite і файли експорту - і більше ні про що.

import csv
import sqlite3
from pathlib import Path

from .models import Note

# таблиця з практичних 3-5; updated_at додано для вікна нотатки
SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    pinned INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT ''
)
"""


class StorageError(Exception):
    # Помилка читання або запису, зрозуміла верхнім шарам.
    pass


def _migrate(connection):
    # Доводить стару базу (з практичної 3 чи 5) до поточної схеми.
    columns = {row[1] for row in connection.execute("PRAGMA table_info(notes)")}

    if "pinned" not in columns:            # база з практичних 3-4
        connection.execute("ALTER TABLE notes ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0")
    if "updated_at" not in columns:        # база з практичної 5
        connection.execute("ALTER TABLE notes ADD COLUMN updated_at TEXT NOT NULL DEFAULT ''")
        connection.execute("UPDATE notes SET updated_at = created_at WHERE updated_at = ''")


class SqliteStorage:
    def __init__(self, path):
        self._path = Path(path)

    @property
    def path(self):
        return self._path

    def load(self):
        if not self._path.exists():
            return []

        connection = None
        try:
            connection = sqlite3.connect(self._path)
            with connection:
                connection.execute(SCHEMA)
                _migrate(connection)
            rows = connection.execute(
                "SELECT id, text, created_at, updated_at, pinned FROM notes ORDER BY id"
            ).fetchall()
        except sqlite3.Error as error:
            raise StorageError(f"Cannot read {self._path.name}: {error}") from error
        finally:
            if connection is not None:
                connection.close()

        try:
            return [Note.from_row(row) for row in rows]
        except ValueError as error:
            raise StorageError(f"Broken record in {self._path.name}: {error}") from error

    def save(self, notes):
        connection = None
        try:
            connection = sqlite3.connect(self._path)
            # with connection = одна транзакція: або записано все, або нічого
            with connection:
                connection.execute(SCHEMA)
                _migrate(connection)
                connection.execute("DELETE FROM notes")
                connection.executemany(
                    "INSERT INTO notes (id, text, created_at, updated_at, pinned) "
                    "VALUES (?, ?, ?, ?, ?)",
                    [note.to_row() for note in notes],
                )
        except sqlite3.Error as error:
            raise StorageError(f"Cannot write {self._path.name}: {error}") from error
        finally:
            if connection is not None:
                connection.close()


def export_notes(notes, path, header):
    # Експорт у TXT або CSV - формат визначається розширенням файла.
    path = Path(path)

    try:
        if path.suffix.lower() == ".csv":
            with open(path, "w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["id", "created_at", "updated_at", "pinned", "text"])
                for note in notes:
                    writer.writerow(
                        [note.id, note.created_at, note.updated_at, int(note.pinned), note.text]
                    )
        else:
            lines = [header, "=" * len(header), ""]
            for note in notes:
                mark = " [pinned]" if note.pinned else ""
                lines.append(f"--- Note {note.id}{mark} ({note.created_at})")
                lines.append(note.text)
                lines.append("")
            path.write_text("\n".join(lines), encoding="utf-8")
    except OSError as error:
        raise StorageError(f"Cannot export to {path}: {error}") from error
