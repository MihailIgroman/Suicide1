"""Перевірки логіки без інтерфейсу: стан, сховище, налаштування.

Запуск: python check_state.py
Кожна перевірка працює в тимчасовому каталозі й нічого не псує.
"""

import logging
import sqlite3
import tempfile
from pathlib import Path

from app import config
from app.settings import AppSettings
from app.state import NO_SELECTION, AppState
from app.storage import SqliteStorage, StorageError

# WARNING-и з навмисно зіпсованих файлів у консоль не потрібні
logging.basicConfig(level=logging.CRITICAL)


def make_state(directory):
    return AppState(SqliteStorage(Path(directory) / "test.db"))


# --- стан -------------------------------------------------------------------

def check_add_and_select(tmp):
    state = make_state(tmp)
    note_id = state.add_note("first")

    assert note_id == 1
    assert state.count() == 1
    assert state.selected_id() == note_id
    assert state.is_dirty() and state.is_note_dirty(note_id)


def check_update_without_change_emits_nothing(tmp):
    state = make_state(tmp)
    note_id = state.add_note("same")
    calls = []
    state.note_updated.connect(calls.append)

    state.update_text(note_id, "same")         # без змін - сигналу немає
    state.update_text(note_id, "other")

    assert calls == [note_id], calls


def check_pinned_first_order(tmp):
    state = make_state(tmp)
    first = state.add_note("a")
    second = state.add_note("b")
    state.set_pinned(second, True)

    assert [n.id for n in state.notes()] == [second, first]
    state.set_pinned_first(False)
    assert [n.id for n in state.notes()] == [first, second]


def check_delete_clears_selection(tmp):
    state = make_state(tmp)
    note_id = state.add_note("x")
    removed = []
    state.note_removed.connect(removed.append)

    state.delete_note(note_id)

    assert state.count() == 0
    assert state.selected_id() == NO_SELECTION
    assert removed == [note_id]


# --- сховище ----------------------------------------------------------------

def check_save_and_load_roundtrip(tmp):
    state = make_state(tmp)
    note_id = state.add_note("hello")
    state.set_pinned(note_id, True)
    assert state.save()
    assert not state.is_dirty()

    again = make_state(tmp)
    again.load()
    note = again.find(note_id)
    assert note is not None and note.text == "hello" and note.pinned
    assert again.add_note() == note_id + 1     # id після завантаження не повторюються


def check_missing_database_is_not_an_error(tmp):
    state = make_state(tmp)
    errors = []
    state.error_occurred.connect(errors.append)

    state.load()

    assert errors == [] and state.count() == 0


def check_corrupted_database(tmp):
    path = Path(tmp) / "test.db"
    path.write_bytes(b"this is not an sqlite file at all" * 100)

    state = make_state(tmp)
    errors = []
    state.error_occurred.connect(errors.append)
    state.load()

    assert len(errors) == 1 and "Cannot read" in errors[0], errors
    assert state.count() == 0                  # застосунок порожній, але робочий

    state.add_note("new")
    assert not state.save()                    # зіпсований файл не перезаписуємо мовчки
    assert state.is_dirty()                    # дані в пам'яті цілі
    assert path.read_bytes().startswith(b"this is not")


def check_bad_record_is_skipped(tmp):
    path = Path(tmp) / "test.db"
    connection = sqlite3.connect(path)
    with connection:
        connection.execute(
            "CREATE TABLE notes (id INTEGER PRIMARY KEY, text TEXT, pinned INTEGER, updated_at TEXT)"
        )
        connection.execute("INSERT INTO notes VALUES (1, 'ok', 0, '')")
        connection.execute("INSERT INTO notes VALUES (2, NULL, 0, '')")   # зіпсований запис
    connection.close()

    notes = SqliteStorage(path).load()
    assert [n.id for n in notes] == [1]


def check_unwritable_location(tmp):
    blocker = Path(tmp) / "blocker"
    blocker.write_text("a file, not a folder")
    storage = SqliteStorage(blocker / "notes.db")  # каталогом є файл - записати неможливо

    try:
        storage.save([])
    except StorageError:
        return
    raise AssertionError("StorageError expected")


def check_export(tmp):
    state = make_state(tmp)
    state.add_note("exported text")
    path = Path(tmp) / "export.txt"

    assert state.export(path, "header")
    assert "exported text" in path.read_text(encoding="utf-8")


# --- налаштування -----------------------------------------------------------

def check_settings_defaults_on_empty_file(tmp):
    path = Path(tmp) / "settings.ini"
    path.write_text("")
    settings = AppSettings(path)

    assert settings.font_size == 12
    assert settings.preview_length == config.TABLE_PREVIEW_LENGTH
    assert settings.autosave is True
    assert settings.autosave_interval_s == 30
    assert settings.confirm_delete is True
    assert settings.log_level == "INFO"
    assert settings.window_geometry().isEmpty()


def check_settings_survive_garbage(tmp):
    path = Path(tmp) / "settings.ini"
    path.write_text(
        "[ui]\nfont_size=abc\npreview_length=900\n"
        "[editor]\nautosave=maybe\nautosave_interval_s=-4\nconfirm_delete=false\n"
        "[logging]\nlevel=LOUD\n[window]\ngeometry=zzz\n"
    )
    settings = AppSettings(path)

    assert settings.font_size == 12               # нечисло -> типове
    assert settings.preview_length == 200         # за межею -> межа
    assert settings.autosave is True              # "maybe" -> типове
    assert settings.autosave_interval_s == 5
    assert settings.confirm_delete is False       # рядок "false" - справді False
    assert settings.log_level == "INFO"
    assert settings.window_geometry().isEmpty()


def check_settings_binary_junk(tmp):
    path = Path(tmp) / "settings.ini"
    path.write_bytes(b"\x00\x01\xff garbage [[[ ===\n")
    settings = AppSettings(path)

    assert settings.values()["font_size"] == 12


def check_settings_apply_emits_once(tmp):
    settings = AppSettings(Path(tmp) / "settings.ini")
    calls = []
    settings.changed.connect(lambda: calls.append(1))

    values = settings.values()
    values.update(font_size=99, log_level="DEBUG", autosave=False)
    settings.apply(values)

    assert calls == [1]
    assert settings.font_size == 32 and settings.log_level == "DEBUG" and not settings.autosave


def check_recent_exports(tmp):
    settings = AppSettings(Path(tmp) / "settings.ini")
    settings.add_recent_export("only.txt")
    # масив QSettings: один елемент не перетворюється на рядок
    assert settings.recent_exports() == ["only.txt"]

    for index in range(config.RECENT_EXPORTS_MAX + 2):
        settings.add_recent_export(f"file{index}.txt")
    settings.add_recent_export("file3.txt")      # повтор піднімається на початок

    recent = settings.recent_exports()
    assert len(recent) == config.RECENT_EXPORTS_MAX
    assert recent[0] == "file3.txt" and recent.count("file3.txt") == 1


def main():
    checks = [
        check_add_and_select,
        check_update_without_change_emits_nothing,
        check_pinned_first_order,
        check_delete_clears_selection,
        check_save_and_load_roundtrip,
        check_missing_database_is_not_an_error,
        check_corrupted_database,
        check_bad_record_is_skipped,
        check_unwritable_location,
        check_export,
        check_settings_defaults_on_empty_file,
        check_settings_survive_garbage,
        check_settings_binary_junk,
        check_settings_apply_emits_once,
        check_recent_exports,
    ]

    for check in checks:
        with tempfile.TemporaryDirectory() as tmp:
            check(tmp)
        print(f"OK: {check.__name__}")

    print(f"{len(checks)} checks passed")


if __name__ == "__main__":
    main()
