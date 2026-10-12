# Панель редагування вибраної нотатки. Зміни йдуть у стан під час набору.

from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget


class NoteEditorPanel(QWidget):
    def __init__(self, state, parent=None):
        super().__init__(parent)

        self.state = state
        self._loading = False         # зараз іде render: не реагувати на textChanged
        self._sending = False         # зміну спричинили ми: не перемальовуватись

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Note text")

        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: gray;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.info_label)

        self.text_edit.textChanged.connect(self.on_text_changed)
        self.state.selection_changed.connect(self.render)
        self.state.notes_changed.connect(self.render)
        self.state.note_updated.connect(self.on_note_updated)

        self.render()

    def on_text_changed(self):
        if self._loading:
            return

        self._sending = True
        try:
            self.state.update_text(self.state.selected_id(), self.text_edit.toPlainText())
        finally:
            self._sending = False
        self.render_info()

    def on_note_updated(self, note_id):
        if note_id != self.state.selected_id():
            return
        if self._sending:
            self.render_info()        # власна зміна: текст не чіпаємо, курсор на місці
            return
        self.render()                 # нотатку змінили з іншого місця

    def render(self, note_id=None):
        note = self.state.selected_note()

        self._loading = True
        try:
            text = note.text if note is not None else ""
            if self.text_edit.toPlainText() != text:
                self.text_edit.setPlainText(text)
        finally:
            self._loading = False     # прапорець знімається навіть при винятку

        self.text_edit.setEnabled(note is not None)
        self.render_info()

    def render_info(self):
        note = self.state.selected_note()
        if note is None:
            self.info_label.setText("No note selected - press New note (Ctrl+N)")
            return

        pinned = "   pinned" if note.pinned else ""
        self.info_label.setText(
            f"Note {note.id}   created {note.created_at}   updated {note.updated_at}{pinned}"
        )
