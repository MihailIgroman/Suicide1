"""Шар стану. QtCore - можна (потрібні сигнали), QtWidgets - ні.

Помилки сховища не вилітають назовні: стан пише їх у лог
і перетворює на сигнал error_occurred.
"""

import logging

from PySide6.QtCore import QObject, Signal

from .models import Note
from .storage import StorageError, export_notes

logger = logging.getLogger(__name__)

NO_SELECTION = -1


class AppState(QObject):
    """Єдине джерело істини для всіх вікон."""

    notes_changed = Signal()          # склад або порядок списку змінився
    note_updated = Signal(int)        # змінився вміст однієї нотатки
    note_removed = Signal(int)        # нотатку видалено: її вікно має закритись
    selection_changed = Signal(int)   # вибрано іншу нотатку
    dirty_changed = Signal(bool)      # з'явились / зникли незбережені зміни
    preferences_changed = Signal()    # змінився порядок показу (pinned first)
    error_occurred = Signal(str)      # дію не вдалося виконати

    def __init__(self, storage, parent=None):
        super().__init__(parent)

        self._storage = storage
        self._notes = []
        self._next_id = 1
        self._selected_id = NO_SELECTION
        self._dirty = False
        self._dirty_ids = set()       # нотатки, змінені після останнього збереження
        self._pinned_first = True

    # ------------------------------------------------------------ читання

    def notes(self):
        """Нотатки в порядку показу: закріплені першими, якщо так налаштовано."""
        if self._pinned_first:
            return tuple(sorted(self._notes, key=lambda note: not note.pinned))
        return tuple(self._notes)

    def count(self):
        return len(self._notes)

    def pinned_count(self):
        return sum(1 for note in self._notes if note.pinned)

    def find(self, note_id):
        for note in self._notes:
            if note.id == note_id:
                return note
        return None

    def selected_id(self):
        return self._selected_id

    def selected_note(self):
        return self.find(self._selected_id)

    def is_dirty(self):
        return self._dirty

    def is_note_dirty(self, note_id):
        return note_id in self._dirty_ids

    def pinned_first(self):
        return self._pinned_first

    # ----------------------------------------------------------- виділення

    def select(self, note_id):
        if note_id == self._selected_id:
            return

        self._selected_id = note_id if self.find(note_id) else NO_SELECTION
        self.selection_changed.emit(self._selected_id)

    # --------------------------------------------------------------- зміна

    def add_note(self, text=""):
        note = Note(id=self._next_id, text=text)
        note.touch()

        self._next_id += 1
        self._notes.append(note)

        self._mark_dirty(note.id)
        self.notes_changed.emit()
        self.select(note.id)

        logger.debug("Note %s added", note.id)
        return note.id

    def update_text(self, note_id, text):
        note = self.find(note_id)
        if note is None or note.text == text:
            return False                  # нічого не змінилось - сигналу немає

        note.text = text
        note.touch()

        self._mark_dirty(note_id)
        self.note_updated.emit(note_id)
        return True

    def set_pinned(self, note_id, pinned):
        note = self.find(note_id)
        if note is None or note.pinned == pinned:
            return False

        note.pinned = pinned
        note.touch()

        self._mark_dirty(note_id)
        if self._pinned_first:
            self.notes_changed.emit()     # порядок рядків змінився
        self.note_updated.emit(note_id)
        return True

    def toggle_pinned(self, note_id):
        note = self.find(note_id)
        if note is None:
            return False
        return self.set_pinned(note_id, not note.pinned)

    def delete_note(self, note_id):
        note = self.find(note_id)
        if note is None:
            return False

        self._notes.remove(note)
        self._dirty_ids.discard(note_id)

        if self._selected_id == note_id:
            self._selected_id = NO_SELECTION
            self.selection_changed.emit(NO_SELECTION)

        self._set_dirty(True)
        self.note_removed.emit(note_id)
        self.notes_changed.emit()

        logger.debug("Note %s deleted", note_id)
        return True

    def set_pinned_first(self, value):
        if self._pinned_first == value:
            return

        self._pinned_first = value
        self.preferences_changed.emit()
        self.notes_changed.emit()

    # --------------------------------------------------------- збереження

    def load(self):
        try:
            self._notes = list(self._storage.load())
        except StorageError as error:
            logger.error("Load failed: %s", error, exc_info=True)
            self._notes = []
            self.error_occurred.emit(str(error))

        # нові нотатки не повинні отримати вже зайняті id
        self._next_id = max((note.id for note in self._notes), default=0) + 1

        self._dirty_ids.clear()
        self._selected_id = NO_SELECTION
        self._set_dirty(False)
        self.notes_changed.emit()
        self.selection_changed.emit(NO_SELECTION)

    def save(self):
        try:
            self._storage.save(self._notes)
        except StorageError as error:
            logger.error("Save failed: %s", error, exc_info=True)
            self.error_occurred.emit(str(error))
            return False              # dirty лишається: дані в пам'яті цілі

        self._dirty_ids.clear()
        self._set_dirty(False)
        return True

    def export(self, path, header):
        try:
            export_notes(self.notes(), path, header)
        except StorageError as error:
            logger.error("Export failed: %s", error, exc_info=True)
            self.error_occurred.emit(str(error))
            return False
        return True

    # ------------------------------------------------------------ приватне

    def _mark_dirty(self, note_id):
        newly_dirty = note_id not in self._dirty_ids
        self._dirty_ids.add(note_id)

        if not self._dirty:
            self._set_dirty(True)
        elif newly_dirty:
            # загальний прапорець не змінився, але зірочка вікна нотатки - так
            self.dirty_changed.emit(True)

    def _set_dirty(self, value):
        if self._dirty == value:
            return

        self._dirty = value
        self.dirty_changed.emit(value)
