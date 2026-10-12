# Модальний діалог налаштувань: OK застосовує, Cancel нічого не змінює.

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)

from ..state import PREVIEW_MAX, PREVIEW_MIN


class PreferencesDialog(QDialog):
    def __init__(self, state, parent=None):
        super().__init__(parent)

        self.state = state
        self.setWindowTitle("Preferences")

        self.pinned_first_box = QCheckBox("Show pinned notes first")
        self.pinned_first_box.setChecked(state.pinned_first())

        # QSpinBox замість QLineEdit: нечисло ввести неможливо, межі гарантовані
        self.preview_spin = QSpinBox()
        self.preview_spin.setRange(PREVIEW_MIN, PREVIEW_MAX)
        self.preview_spin.setValue(state.preview_length())

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        form = QFormLayout()
        form.addRow("Preview length:", self.preview_spin)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Applies to every open window."))
        layout.addWidget(self.pinned_first_box)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def accept(self):
        # стан змінюємо тільки після підтвердження: Cancel має нічого не робити
        self.state.set_preferences(self.pinned_first_box.isChecked(), self.preview_spin.value())
        super().accept()
