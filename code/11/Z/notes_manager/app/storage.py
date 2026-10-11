"""Шар збереження: SQLite і експорт у текстовий файл.

Усі помилки нижнього рівня (sqlite3.Error, OSError) перекладаються
в StorageError - верхні шари ловлять тільки її.
"""

import logging
import os
import sqlite3
from pathlib import Path

from .models import Note

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER PRIMARY KEY,
    text       TEXT    NOT NULL DEFAULT '',
    pinned     INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT    NOT NULL DEFAULT ''
)
"""


class StorageError(Exception):
    """Помилка читання або запису, зрозуміла верхнім шарам."""


class SqliteStorage:
    def __init__(self, path):
        self._path = Path(path)

    @property
    def path(self):
        return self._path

    def load(self):
        if not self._path.exists():
            # відсутня база - не помилка, а перший запуск
            logger.info("No database yet, starting empty: %s", self._path)
            return []

        connection = None
        try:
            connection = sqlite3.connect(self._path, timeout=5)
            connection.execute(SCHEMA)
            rows = connection.execute(
                "SELECT id, text, pinned, updated_at FROM notes ORDER BY id"
            ).fetchall()
        except sqlite3.Error as error:
            # сюди потрапляє і "file is not a database", і чужа схема таблиці
            raise StorageError(
                f"Cannot read the database {self._path.name}: {error}. "
                "The file is left untouched; rename or remove it to start a new database."
            ) from error
        finally:
            if connection is not None:
                connection.close()

        notes = []
        for row in rows:
            try:
                notes.append(Note.from_row(row))
            except ValueError:
                # один зіпсований запис не має коштувати всієї бази
                logger.warning("Skipping bad record: %r", row, exc_info=True)

        logger.info("Loaded %s notes from %s", len(notes), self._path)
        return notes

    def save(self, notes):
        self._backup()

        connection = None
        try:
            connection = sqlite3.connect(self._path, timeout=5)
            # with connection = одна транзакція: або записано все, або нічого
            with connection:
                connection.execute(SCHEMA)
                connection.execute("DELETE FROM notes")
                connection.executemany(
                    "INSERT INTO notes (id, text, pinned, updated_at) VALUES (?, ?, ?, ?)",
                    [note.to_row() for note in notes],
                )
        except sqlite3.Error as error:
            raise StorageError(
                f"Cannot save notes to {self._path}: {error}. "
                "Check that the folder is writable and the file is not damaged."
            ) from error
        finally:
            if connection is not None:
                connection.close()

        logger.info("Saved %s notes to %s", len(notes), self._path)

    def _backup(self):
        """Копія бази перед записом: <db>.bak. Невдача - не привід не зберігати."""
        if not self._path.exists():
            return

        backup_path = self._path.with_name(self._path.name + ".bak")
        source = target = None
        try:
            source = sqlite3.connect(self._path, timeout=5)
            target = sqlite3.connect(backup_path)
            source.backup(target)
        except sqlite3.Error as error:
            logger.warning("Backup skipped (%s): %s", backup_path, error)
        finally:
            for connection in (source, target):
                if connection is not None:
                    connection.close()


def export_notes(notes, path, header):
    """Пише нотатки в текстовий файл атомарно: .tmp, потім os.replace."""
    path = Path(path)
    temp_path = path.with_name(path.name + ".tmp")

    lines = [header, "=" * len(header), ""]
    for note in notes:
        mark = " [pinned]" if note.pinned else ""
        lines.append(f"--- Note {note.id}{mark} ({note.updated_at})")
        lines.append(note.text)
        lines.append("")

    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_path, path)
    except OSError as error:
        raise StorageError(f"Cannot export to {path}: {error}") from error
    finally:
        temp_path.unlink(missing_ok=True)

    logger.info("Exported %s notes to %s", len(notes), path)
