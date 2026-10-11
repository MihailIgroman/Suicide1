"""Перехідник між AppState і QTableView. Власних даних не тримає.

self._notes - знімок ПОРЯДКУ рядків (ті самі об'єкти Note, що й у стані),
а не копія даних. Номер рядка перетворюється на id лише тут.
"""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QFont

from .. import config


class NoteTableModel(QAbstractTableModel):
    COLUMNS = ["ID", "Pinned", "Preview", "Chars", "Updated"]
    COL_ID, COL_PINNED, COL_PREVIEW, COL_CHARS, COL_UPDATED = range(5)

    def __init__(self, state, preview_length, parent=None):
        super().__init__(parent)

        self._state = state
        self._preview_length = preview_length
        self._notes = list(state.notes())

        state.notes_changed.connect(self._reload)
        state.note_updated.connect(self._on_note_updated)

    # ------------------------------------------------- обов'язковий мінімум

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._notes)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.COLUMNS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        note = self._notes[index.row()]
        column = index.column()
        is_long = note.is_long(config.LONG_NOTE_CHARS)

        if role == Qt.ItemDataRole.DisplayRole:
            if column == self.COL_ID:
                return note.id
            if column == self.COL_PREVIEW:
                return note.preview(self._preview_length)
            if column == self.COL_CHARS:
                return len(note.text)
            if column == self.COL_UPDATED:
                return note.updated_at
            return None                        # у колонці з галочкою тексту немає

        if role == Qt.ItemDataRole.EditRole:
            # значення для сортування: числа - числами, а не рядками
            if column == self.COL_ID:
                return note.id
            if column == self.COL_PINNED:
                return int(note.pinned)
            if column == self.COL_PREVIEW:
                return note.text.lower()
            if column == self.COL_CHARS:
                return len(note.text)
            return note.updated_at

        if role == Qt.ItemDataRole.CheckStateRole and column == self.COL_PINNED:
            return Qt.CheckState.Checked if note.pinned else Qt.CheckState.Unchecked

        if role == Qt.ItemDataRole.FontRole and (note.pinned or is_long):
            font = QFont()
            font.setBold(note.pinned)
            font.setItalic(is_long)
            return font

        if role == Qt.ItemDataRole.ToolTipRole:
            if is_long:
                return f"Long note: {len(note.text)} chars"
            return note.text[:200] if note.text else "Empty note"

        if role == Qt.ItemDataRole.TextAlignmentRole and column in (self.COL_ID, self.COL_CHARS):
            return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.COLUMNS[section]
        return section + 1

    # -------------------------------------------------------- редагування

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() == self.COL_PINNED:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        return flags

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False

        if role == Qt.ItemDataRole.CheckStateRole and index.column() == self.COL_PINNED:
            note = self._notes[index.row()]
            checked = Qt.CheckState(value) == Qt.CheckState.Checked
            # зміну робить стан; він же надішле note_updated -> dataChanged
            return self._state.set_pinned(note.id, checked)

        return False

    # ------------------------------------------------------ налаштування

    def set_preview_length(self, length):
        if length == self._preview_length:
            return

        self._preview_length = length
        if self._notes:
            top = self.index(0, self.COL_PREVIEW)
            bottom = self.index(len(self._notes) - 1, self.COL_PREVIEW)
            self.dataChanged.emit(top, bottom)

    # ------------------------------------------------------ рядок <-> id

    def note_id_at(self, row):
        if 0 <= row < len(self._notes):
            return self._notes[row].id
        return None

    def row_of(self, note_id):
        for row, note in enumerate(self._notes):
            if note.id == note_id:
                return row
        return -1

    # ------------------------------------------------- реакція на стан

    def _reload(self):
        self.beginResetModel()
        try:
            self._notes = list(self._state.notes())
        finally:
            self.endResetModel()

    def _on_note_updated(self, note_id):
        row = self.row_of(note_id)
        if row < 0:
            return

        left = self.index(row, 0)
        right = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(left, right)
