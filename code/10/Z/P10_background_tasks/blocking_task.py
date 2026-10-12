import sys
import time

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

STUDENT_NAME = "Andrii Zelyuk"      # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"             # група
APP_TITLE = "Task Demo"             # назва застосунку
STEP_COUNT = 10                     # скільки кроків у роботі
SLEEP_MS = 500                      # пауза на кожному кроці, мілісекунд


class TaskWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_TITLE} - {STUDENT_NAME}, {STUDENT_GROUP}")

        self.clicks = 0

        self.status_label = QLabel("Ready")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, STEP_COUNT)
        self.progress_bar.setValue(0)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_task)

        # "датчик життя" вікна: лише рахує клацання
        self.click_button = QPushButton("Click me (0)")
        self.click_button.clicked.connect(self.count_click)

        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.start_button)
        layout.addWidget(self.click_button)

    def start_task(self):
        self.start_button.setEnabled(False)
        self.status_label.setText("Working...")
        self.progress_bar.setValue(0)

        # ПОГАНО навмисно: довга робота прямо в слоті кнопки.
        # Поки цикл крутиться, цикл подій Qt стоїть: вікно не перемальовується,
        # клацання не обробляються, перетягнути вікно неможливо.
        for step in range(1, STEP_COUNT + 1):
            time.sleep(SLEEP_MS / 1000)
            self.progress_bar.setValue(step)

        self.status_label.setText("Done")
        self.start_button.setEnabled(True)

    def count_click(self):
        self.clicks += 1
        self.click_button.setText(f"Click me ({self.clicks})")


def main():
    app = QApplication(sys.argv)

    window = TaskWindow()
    window.resize(360, 180)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
