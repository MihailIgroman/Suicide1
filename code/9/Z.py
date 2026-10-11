import sys
from pathlib import Path
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

BASE_DIR = Path(__file__).resolve().parent


class ResourceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Зелюк Андрій (Варіант 6)")

        frozen = getattr(sys, "frozen", False)
        img_path = BASE_DIR / "assets" / "logo.png"

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Студент: Зелюк Андрій (Варіант 6)"))
        layout.addWidget(QLabel(f"Режим frozen: {frozen}"))
        layout.addWidget(QLabel(f"Робочий каталог: {BASE_DIR}"))

        img_label = QLabel()
        pixmap = QPixmap(str(img_path))

        if not pixmap.isNull():
            img_label.setPixmap(pixmap)
            layout.addWidget(img_label)
        else:
            img_label.setText(f"Файл не знайдено: {img_path}")
            layout.addWidget(img_label)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResourceWindow()
    window.show()
    sys.exit(app.exec())