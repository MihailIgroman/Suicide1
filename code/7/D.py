import sys
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Практична 7 — Джусь Андрій (Варіант 5)")
        self.resize(320, 160)

        self.label = QLabel("Студент: Джусь Андрій (Варіант 5)")
        self.button = QPushButton("Переключити стан")
        self.button.clicked.connect(self._toggle_state)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def _toggle_state(self):
        if self.label.text() == "Студент: Джусь Андрій (Варіант 5)":
            self.label.setText("Стан: Заявка Джуся Андрія прийнята")
        else:
            self.label.setText("Студент: Джусь Андрій (Варіант 5)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())