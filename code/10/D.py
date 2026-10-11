import sys
from pathlib import Path
from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def get_save_path() -> Path:
    # ✅ Передаємо enum QStandardPaths.StandardLocation.AppDataLocation у метод writableLocation()
    base_path = Path(
        QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )
    ) / "Dhus_V5_Data"
    base_path.mkdir(parents=True, exist_ok=True)
    return base_path / "user_config.txt"


class StorageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Джусь Андрій (Варіант 5)")
        self.file_path = get_save_path()

        self.info_label = QLabel("Автор: Джусь Андрій")
        self.input_field = QLineEdit()
        self.btn_save = QPushButton("Зберегти конфіг")
        self.btn_save.clicked.connect(self._save_data)

        layout = QVBoxLayout(self)
        layout.addWidget(self.info_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.btn_save)

        self._load_data()

    def _load_data(self):
        if self.file_path.exists():
            content = self.file_path.read_text(encoding="utf-8")
            self.input_field.setText(content)

    def _save_data(self):
        self.file_path.write_text(self.input_field.text(), encoding="utf-8")
        QMessageBox.information(
            self, "Збережено", f"Файл Джуся А. успішно збережено у:\n{self.file_path}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StorageApp()
    window.show()
    sys.exit(app.exec())