# Панель зі списком нотаток. Своїх даних не тримає: усе бере зі стану.

from PySide6.QtCore import QSignalBlocker, Qt, Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from ..state import NO_SELECTION

NOTE_ID_ROLE = Qt.ItemDataRole.UserRole


class NoteListPanel(QWidget):
    open_requested = Signal(int)      # подвійне клацання: відкрити нотатку у вікні

    def __init__(self, state, parent=None):
        super().__init__(parent)

        self.state = state

        self.list_widget = QListWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.list_widget)

        self.list_widget.currentItemChanged.connect(self.on_current_item_changed)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

        self.state.notes_changed.connect(self.render)
        self.state.note_updated.connect(self.on_note_updated)
        self.state.selection_changed.connect(self.render_selection)
        self.state.preferences_changed.connect(self.render)

        self.render()

    # --- наміри користувача ---

    def on_current_item_changed(self, current, previous):
        if current is None:
            self.state.select(NO_SELECTION)
        else:
            self.state.select(current.data(NOTE_ID_ROLE))

    def on_item_double_clicked(self, widget_item):
        self.open_requested.emit(widget_item.data(NOTE_ID_ROLE))

    # --- перемальовування ---

    def _item_text(self, note):
        mark = "[P] " if note.pinned else ""
        return f"{mark}{note.preview(self.state.preview_length())}"

    def _apply_look(self, widget_item, note):
        widget_item.setText(self._item_text(note))
        font = widget_item.font()
        font.setBold(note.pinned)
        widget_item.setFont(font)
        widget_item.setToolTip(f"Created: {note.created_at}\nUpdated: {note.updated_at}")

    def on_note_updated(self, note_id):
        # Змінилась одна нотатка - оновлюємо один рядок, а не весь список.
        note = self.state.find(note_id)
        if note is None:
            return

        for row in range(self.list_widget.count()):
            widget_item = self.list_widget.item(row)
            if widget_item.data(NOTE_ID_ROLE) == note_id:
                self._apply_look(widget_item, note)
                return

    def render(self):
        with QSignalBlocker(self.list_widget):
            self.list_widget.clear()

            for note in self.state.visible_notes():
                widget_item = QListWidgetItem()
                widget_item.setData(NOTE_ID_ROLE, note.id)     # id, а не номер рядка
                self._apply_look(widget_item, note)
                self.list_widget.addItem(widget_item)

        self.render_selection()

    def render_selection(self, note_id=None):
        selected_id = self.state.selected_id()

        with QSignalBlocker(self.list_widget):
            self.list_widget.setCurrentRow(-1)

            for row in range(self.list_widget.count()):
                if self.list_widget.item(row).data(NOTE_ID_ROLE) == selected_id:
                    self.list_widget.setCurrentRow(row)
                    break
