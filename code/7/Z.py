import sys
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Практична 7 — Зелюк Андрій (Варіант 6)")
        self.resize(340, 160)
        self.counter = 0

        self.label = QLabel("Зелюк Андрій (Варіант 6) | Лічильник: 0")
        self.btn_add = QPushButton("Додати лічильник")
        self.btn_exit = QPushButton("Завершити")

        self.btn_add.clicked.connect(self._increment)
        self.btn_exit.clicked.connect(self.close)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_exit)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addLayout(btn_layout)

    def _increment(self):
        self.counter += 1
        self.label.setText(f"Зелюк Андрій (Варіант 6) | Лічильник: {self.counter}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())