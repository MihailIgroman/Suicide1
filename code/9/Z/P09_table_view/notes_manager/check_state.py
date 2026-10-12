# Перевірки логіки без інтерфейсу.
#
# Запуск: python check_state.py
# Кожна перевірка працює з базою в тимчасовому каталозі й нічого не псує.

import sqlite3
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt

from app.state import FILTER_ALL, FILTER_OTHER, FILTER_PINNED, NO_SELECTION, AppState
from app.storage import SqliteStorage
from app.ui.note_table_model import NoteTableModel


def make_state(directory):
    return AppState(SqliteStorage(Path(directory) / "test.db"))


def check_add_selects_new_note(tmp):
    state = make_state(tmp)
    note_id = state.add_note("first")

    assert note_id == 1
    assert state.count() == 1
    assert state.selected_id() == note_id
    assert state.is_dirty()


def check_update_without_change_emits_nothing(tmp):
    state = make_state(tmp)
    note_id = state.add_note("same")
    calls = []
    state.note_updated.connect(calls.append)

    state.update_text(note_id, "same")         # без змін - сигналу немає
    state.update_text(note_id, "other")

    assert calls == [note_id], calls


def check_dirty_signal_once(tmp):
    state = make_state(tmp)
    calls = []
    state.dirty_changed.connect(calls.append)

    note_id = state.add_note("a")
    state.update_text(note_id, "b")            # уже dirty - сигналу немає

    assert calls == [True], calls


def check_filter(tmp):
    state = make_state(tmp)
    first = state.add_note("a")
    second = state.add_note("b")
    state.set_pinned(second, True)

    state.set_filter(FILTER_PINNED)
    assert [n.id for n in state.visible_notes()] == [second]
    state.set_filter(FILTER_OTHER)
    assert [n.id for n in state.visible_notes()] == [first]

    # нова нотатка під фільтром Pinned повертає фільтр на All
    state.set_filter(FILTER_PINNED)
    state.add_note("c")
    assert state.current_filter() == FILTER_ALL


def check_delete_and_clear(tmp):
    state = make_state(tmp)
    first = state.add_note("a")
    state.add_note("b")

    state.select(first)
    state.delete_note(first)
    assert state.count() == 1 and state.selected_id() == NO_SELECTION

    state.clear_all()
    assert state.count() == 0


def check_save_and_load(tmp):
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


def check_old_database_is_migrated(tmp):
    # база з практичної 3: ні pinned, ні updated_at
    path = Path(tmp) / "test.db"
    connection = sqlite3.connect(path)
    with connection:
        connection.execute(
            "CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "text TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO notes (text, created_at) VALUES (?, ?)", ("old note", "2026-08-19 14:05")
        )
    connection.close()

    state = make_state(tmp)
    state.load()
    note = state.notes()[0]
    assert note.text == "old note" and not note.pinned
    assert note.updated_at == "2026-08-19 14:05"


def check_export(tmp):
    state = make_state(tmp)
    state.add_note("exported, with comma")

    txt = Path(tmp) / "out.txt"
    csv_path = Path(tmp) / "out.csv"
    assert state.export(txt, "header") and state.export(csv_path, "header")
    assert "exported, with comma" in txt.read_text(encoding="utf-8")
    assert '"exported, with comma"' in csv_path.read_text(encoding="utf-8")


def check_broken_database_reports_error(tmp):
    (Path(tmp) / "test.db").write_bytes(b"not a database" * 100)
    state = make_state(tmp)
    errors = []
    state.error_occurred.connect(errors.append)

    state.load()

    assert len(errors) == 1 and state.count() == 0


# --- практична 8: налаштування й кілька вікон --------------------------------

def check_pinned_first_order(tmp):
    state = make_state(tmp)
    first = state.add_note("a")
    second = state.add_note("b")
    state.set_pinned(second, True)

    assert [n.id for n in state.notes()] == [second, first]
    state.set_preferences(False, state.preview_length())
    assert [n.id for n in state.notes()] == [first, second]


def check_preferences_clamped_and_signal_once(tmp):
    state = make_state(tmp)
    calls = []
    state.preferences_changed.connect(lambda: calls.append(1))

    state.set_preferences(True, 999)               # за межею -> межа
    state.set_preferences(True, 999)               # без змін - сигналу немає

    assert state.preview_length() == 200
    assert calls == [1], calls


def check_note_removed_signal(tmp):
    state = make_state(tmp)
    first = state.add_note("a")
    second = state.add_note("b")
    removed = []
    state.note_removed.connect(removed.append)

    state.delete_note(first)
    state.clear_all()

    assert removed == [first, second], removed


def check_per_note_dirty(tmp):
    state = make_state(tmp)
    first = state.add_note("a")
    assert state.save()
    second = state.add_note("b")

    assert not state.is_note_dirty(first)          # зірочка лише у зміненої нотатки
    assert state.is_note_dirty(second)
    state.save()
    assert not state.is_note_dirty(second)


# --- практична 9: модель таблиці ---------------------------------------------

def check_model_follows_state(tmp):
    state = make_state(tmp)
    model = NoteTableModel(state)
    first = state.add_note("first")
    state.add_note("second")

    assert model.rowCount() == 2
    assert model.note_id_at(model.row_of(first)) == first     # рядок <-> id

    state.set_filter(FILTER_PINNED)
    assert model.rowCount() == 0                              # фільтр бере зі стану


def check_one_note_change_does_not_reset_model(tmp):
    state = make_state(tmp)
    model = NoteTableModel(state)
    note_id = state.add_note("text")
    resets, changes = [], []
    model.modelReset.connect(lambda: resets.append(1))
    model.dataChanged.connect(lambda top, bottom: changes.append(top.row()))

    state.update_text(note_id, "new text")

    assert resets == [] and changes == [model.row_of(note_id)]
    # модель не тримає копії: текст береться з того самого об'єкта Note
    index = model.index(0, NoteTableModel.COL_CHARS)
    assert model.data(index) == len("new text")


def check_pin_through_model_goes_to_state(tmp):
    state = make_state(tmp)
    model = NoteTableModel(state)
    note_id = state.add_note("x")

    index = model.index(model.row_of(note_id), NoteTableModel.COL_PINNED)
    assert model.setData(index, 2, Qt.ItemDataRole.CheckStateRole)   # 2 = Checked
    assert state.find(note_id).pinned


def main():
    checks = [
        check_add_selects_new_note,
        check_update_without_change_emits_nothing,
        check_dirty_signal_once,
        check_filter,
        check_delete_and_clear,
        check_save_and_load,
        check_old_database_is_migrated,
        check_export,
        check_broken_database_reports_error,
        check_pinned_first_order,
        check_preferences_clamped_and_signal_once,
        check_note_removed_signal,
        check_per_note_dirty,
        check_model_follows_state,
        check_one_note_change_does_not_reset_model,
        check_pin_through_model_goes_to_state,
    ]

    for check in checks:
        with tempfile.TemporaryDirectory() as tmp:
            check(tmp)
        print(f"OK: {check.__name__}")

    print(f"{len(checks)} checks passed")


if __name__ == "__main__":
    main()
