import sys
from pathlib import Path
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

BASE_DIR = Path(__file__).resolve().parent


class ResourceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Джусь Андрій (Варіант 5)")

        img_path = BASE_DIR / "assets" / "logo.png"

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Розробник: Джусь Андрій (Варіант 5)"))

        img_label = QLabel()
        pixmap = QPixmap(str(img_path))

        if not pixmap.isNull():
            img_label.setPixmap(pixmap.scaledToWidth(250))
            layout.addWidget(img_label)
        else:
            layout.addWidget(QLabel(f"Помилка завантаження ресурсу: {img_path}"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResourceWindow()
    window.show()
    sys.exit(app.exec())