import json
import sys
from pathlib import Path
from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class JsonStorageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Зелюк Андрій (Варіант 6)")

        app_dir = Path(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppDataLocation
            )
        ) / "Zelyuk_V6_Data"
        app_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = app_dir / "settings.json"

        self.header_label = QLabel("Студент: Зелюк Андрій (Варіант 6)")
        self.status_label = QLabel(f"Шлях: {self.config_path}")
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Введіть параметр конфігурації")

        self.btn_save = QPushButton("Зберегти в JSON")
        self.btn_save.clicked.connect(self._save_config)

        layout = QVBoxLayout(self)
        layout.addWidget(self.header_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.input_user)
        layout.addWidget(self.btn_save)

        self._load_config()

    def _load_config(self):
        if self.config_path.exists():
            try:
                data = json.loads(self.config_path.read_text(encoding="utf-8"))
                self.input_user.setText(data.get("value", ""))
            except json.JSONDecodeError:
                pass

    def _save_config(self):
        data = {
            "student": "Зелюк Андрій",
            "variant": 6,
            "value": self.input_user.text(),
        }
        self.config_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        self.status_label.setText("Конфігурацію Зелюка А. збережено!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JsonStorageApp()
    window.show()
    sys.exit(app.exec())