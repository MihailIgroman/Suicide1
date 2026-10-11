"""Модальний діалог налаштувань.

Про QSettings і про головне вікно не знає: словник усередину, словник назовні.
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)


class PreferencesDialog(QDialog):
    def __init__(self, values, limits, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Preferences")
        self.setModal(True)

        self.pinned_first_box = QCheckBox("Show pinned notes first")
        self.pinned_first_box.setChecked(values["pinned_first"])

        # QSpinBox замість QLineEdit: нечисло ввести неможливо, межі гарантовані
        self.preview_spin = QSpinBox()
        self.preview_spin.setRange(*limits["preview_length"])
        self.preview_spin.setValue(values["preview_length"])

        self.font_spin = QSpinBox()
        self.font_spin.setRange(*limits["font_size"])
        self.font_spin.setSuffix(" pt")
        self.font_spin.setValue(values["font_size"])

        self.autosave_box = QCheckBox("Save changes automatically")
        self.autosave_box.setChecked(values["autosave"])

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(*limits["autosave_interval_s"])
        self.interval_spin.setSuffix(" s")
        self.interval_spin.setValue(values["autosave_interval_s"])
        self.interval_spin.setEnabled(values["autosave"])

        self.confirm_box = QCheckBox("Ask before deleting a note")
        self.confirm_box.setChecked(values["confirm_delete"])

        self.log_combo = QComboBox()
        self.log_combo.addItems(limits["log_level"])
        self.log_combo.setCurrentText(values["log_level"])

        # залежне поле вимикається, поки автозбереження вимкнене
        self.autosave_box.toggled.connect(self.interval_spin.setEnabled)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        form = QFormLayout()
        form.addRow("", self.pinned_first_box)
        form.addRow("Preview length:", self.preview_spin)
        form.addRow("Font size:", self.font_spin)
        form.addRow("", self.autosave_box)
        form.addRow("Autosave every:", self.interval_spin)
        form.addRow("", self.confirm_box)
        form.addRow("Log level:", self.log_combo)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Applies to every open window."))
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self):
        return {
            "pinned_first": self.pinned_first_box.isChecked(),
            "preview_length": self.preview_spin.value(),
            "font_size": self.font_spin.value(),
            "autosave": self.autosave_box.isChecked(),
            "autosave_interval_s": self.interval_spin.value(),
            "confirm_delete": self.confirm_box.isChecked(),
            "log_level": self.log_combo.currentText(),
        }
