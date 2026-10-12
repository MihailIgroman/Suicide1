# Шар стану. QtCore - можна (потрібні сигнали), QtWidgets - ні.
#
# Один AppState на весь застосунок: усі вікна читають його й
# перемальовуються за його сигналами, тому синхронізувати вікна
# між собою не потрібно.

from PySide6.QtCore import QObject, Signal

from .models import Note, now_text
from .storage import StorageError, export_notes

NO_SELECTION = -1

FILTER_ALL = "all"
FILTER_PINNED = "pinned"
FILTER_OTHER = "other"
FILTERS = (FILTER_ALL, FILTER_PINNED, FILTER_OTHER)

PREVIEW_MIN = 10                      # межі довжини підпису у списку
PREVIEW_MAX = 200


class AppState(QObject):
    # Єдине джерело істини для всіх вікон.

    notes_changed = Signal()          # склад або порядок списку змінився
    note_updated = Signal(int)        # змінився вміст однієї нотатки
    note_removed = Signal(int)        # нотатку видалено: її вікно має закритись
    selection_changed = Signal(int)   # вибрано іншу нотатку
    dirty_changed = Signal(bool)      # з'явились / зникли незбережені зміни
    filter_changed = Signal(str)      # змінився фільтр All / Pinned / Other
    preferences_changed = Signal()    # змінились налаштування показу
    error_occurred = Signal(str)      # дію не вдалося виконати

    def __init__(self, storage, preview_length=30, parent=None):
        super().__init__(parent)

        self._storage = storage
        self._notes = []
        self._next_id = 1
        self._selected_id = NO_SELECTION
        self._dirty = False
        self._dirty_ids = set()       # нотатки, змінені після останнього збереження
        self._filter = FILTER_ALL

        # налаштування показу (діалог Preferences)
        self._pinned_first = True
        self._preview_length = preview_length

    # ------------------------------------------------------------ читання

    def notes(self):
        # Усі нотатки в порядку показу: закріплені першими, якщо так налаштовано.
        if self._pinned_first:
            # sorted стабільний: усередині груп лишається порядок за id
            return tuple(sorted(self._notes, key=lambda note: not note.pinned))
        return tuple(self._notes)

    def visible_notes(self):
        # Нотатки, які пропускає поточний фільтр.
        return tuple(note for note in self.notes() if self._passes_filter(note))

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

    def current_filter(self):
        return self._filter

    def pinned_first(self):
        return self._pinned_first

    def preview_length(self):
        return self._preview_length

    # ----------------------------------------------------------- виділення

    def select(self, note_id):
        if note_id == self._selected_id:
            return

        self._selected_id = note_id if self.find(note_id) else NO_SELECTION
        self.selection_changed.emit(self._selected_id)

    # --------------------------------------------------------------- зміна

    def add_note(self, text=""):
        created = now_text()
        note = Note(id=self._next_id, text=text, created_at=created, updated_at=created)

        self._next_id += 1
        self._notes.append(note)

        # нова нотатка не закріплена: під фільтром Pinned її не було б видно
        if not self._passes_filter(note):
            self.set_filter(FILTER_ALL)

        self._mark_dirty(note.id)
        self.notes_changed.emit()
        self.select(note.id)
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

        if self._pinned_first or self._filter != FILTER_ALL:
            # змінився порядок рядків або нотатка зникла з фільтра
            if note_id == self._selected_id and not self._passes_filter(note):
                self.select(NO_SELECTION)
            self.notes_changed.emit()
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
        return True

    def clear_all(self):
        if not self._notes:
            return False

        removed = [note.id for note in self._notes]
        self._notes.clear()
        self._dirty_ids.clear()
        self.select(NO_SELECTION)

        self._set_dirty(True)
        for note_id in removed:
            self.note_removed.emit(note_id)
        self.notes_changed.emit()
        return True

    def set_filter(self, name):
        if name not in FILTERS:
            raise ValueError(f"Unknown filter: {name}")
        if name == self._filter:
            return

        self._filter = name

        selected = self.selected_note()
        if selected is not None and not self._passes_filter(selected):
            self.select(NO_SELECTION)

        self.filter_changed.emit(name)
        self.notes_changed.emit()

    def set_preferences(self, pinned_first, preview_length):
        preview_length = min(max(int(preview_length), PREVIEW_MIN), PREVIEW_MAX)
        if (pinned_first, preview_length) == (self._pinned_first, self._preview_length):
            return

        order_changed = pinned_first != self._pinned_first
        self._pinned_first = pinned_first
        self._preview_length = preview_length

        self.preferences_changed.emit()
        if order_changed:
            self.notes_changed.emit()

    # --------------------------------------------------------- збереження

    def load(self):
        try:
            self._notes = list(self._storage.load())
        except StorageError as error:
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
            self.error_occurred.emit(str(error))
            return False              # dirty лишається: дані в пам'яті цілі

        self._dirty_ids.clear()
        self._set_dirty(False)
        return True

    def export(self, path, header):
        try:
            export_notes(self.notes(), path, header)
        except StorageError as error:
            self.error_occurred.emit(str(error))
            return False
        return True

    # ------------------------------------------------------------ приватне

    def _passes_filter(self, note):
        if self._filter == FILTER_PINNED:
            return note.pinned
        if self._filter == FILTER_OTHER:
            return not note.pinned
        return True

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
