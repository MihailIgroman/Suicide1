"""Немодальне вікно однієї нотатки. Головного вікна не знає: працює зі станом."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .. import config


class NoteWindow(QWidget):
    closed = Signal(int)

    def __init__(self, state, note_id):
        super().__init__()                 # без батька - вікно верхнього рівня

        self.state = state
        self.note_id = note_id

        self._loading = False
        self._sending = False

        self.header_label = QLabel(f"Note {note_id}")
        self.pinned_box = QCheckBox("Pinned")
        self.text_edit = QTextEdit()
        self.updated_label = QLabel()
        close_button = QPushButton("Close")

        top = QHBoxLayout()
        top.addWidget(self.header_label)
        top.addStretch()
        top.addWidget(self.pinned_box)

        bottom = QHBoxLayout()
        bottom.addWidget(self.updated_label)
        bottom.addStretch()
        bottom.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.text_edit)
        layout.addLayout(bottom)

        close_button.clicked.connect(self.close)
        self.text_edit.textChanged.connect(self.on_text_changed)
        self.pinned_box.toggled.connect(self.on_pinned_toggled)

        self.state.note_updated.connect(self.on_note_updated)
        self.state.dirty_changed.connect(self.render_title)

        self.render()

    def set_font_size(self, size):
        font = self.text_edit.font()
        font.setPointSize(size)
        self.text_edit.setFont(font)

    # --- наміри користувача ---

    def on_text_changed(self):
        if self._loading:
            return

        self._sending = True
        try:
            self.state.update_text(self.note_id, self.text_edit.toPlainText())
        finally:
            self._sending = False

    def on_pinned_toggled(self, checked):
        if self._loading:
            return
        self.state.set_pinned(self.note_id, checked)

    # --- перемальовування ---

    def on_note_updated(self, note_id):
        if note_id != self.note_id:
            return
        if self._sending:
            self.render_meta()
            return
        self.render()

    def render(self):
        note = self.state.find(self.note_id)
        if note is None:
            return

        self._loading = True
        try:
            if self.text_edit.toPlainText() != note.text:
                self.text_edit.setPlainText(note.text)
            self.pinned_box.setChecked(note.pinned)
        finally:
            self._loading = False

        self.render_meta()

    def render_meta(self):
        note = self.state.find(self.note_id)
        if note is None:
            return

        self._loading = True
        try:
            self.pinned_box.setChecked(note.pinned)
        finally:
            self._loading = False

        self.updated_label.setText(f"Updated: {note.updated_at}")
        self.render_title()

    def render_title(self, dirty=None):
        mark = "*" if self.state.is_note_dirty(self.note_id) else ""
        self.setWindowTitle(f"Note {self.note_id}{mark} - {config.APP_TITLE}")

    def closeEvent(self, event):
        self.closed.emit(self.note_id)
        super().closeEvent(event)
