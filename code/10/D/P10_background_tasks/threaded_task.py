import sys

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

STUDENT_NAME = "Andrii Dzhus"      # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"             # група
APP_TITLE = "Task Demo"             # назва застосунку
STEP_COUNT = 10                     # скільки кроків у роботі
SLEEP_MS = 500                      # пауза на кожному кроці, мілісекунд


class Worker(QObject):
    # Довга робота. Жодного віджета всередині й жодного імпорту з QtWidgets.

    progress = Signal(int)          # номер виконаного кроку
    finished = Signal()             # робота скінчилась

    @Slot()
    def run(self):
        thread = QThread.currentThread()

        for step in range(1, STEP_COUNT + 1):
            # вікно закривають: виходимо з циклу, не чекаючи всіх кроків
            if thread.isInterruptionRequested():
                break

            # пауза фонового потоку; головний потік у цей час вільний
            thread.msleep(SLEEP_MS)
            self.progress.emit(step)

        self.finished.emit()


class TaskWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_TITLE} - {STUDENT_NAME}, {STUDENT_GROUP}")

        # посилання в полях вікна, а не в локальних змінних: інакше Python
        # знищить об'єкти після виходу з start_task(), і застосунок упаде
        self.thread = None
        self.worker = None
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

        # 1. потік і воркер - два різні об'єкти
        self.thread = QThread()
        self.worker = Worker()

        # 2. воркер переїжджає в потік: його слоти виконуватимуться там
        self.worker.moveToThread(self.thread)

        # 3. старт потоку запускає роботу воркера
        self.thread.started.connect(self.worker.run)

        # 4. результати повертаються у вікно сигналами (у головний потік)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)

        # 5. робота скінчилась - зупиняємо цикл подій потоку
        self.worker.finished.connect(self.thread.quit)

        self.thread.start()

    @Slot(int)
    def on_progress(self, step):
        # слот вікна виконується в головному потоці - віджети чіпати можна
        self.progress_bar.setValue(step)

    @Slot()
    def on_finished(self):
        self.status_label.setText("Done")
        self.start_button.setEnabled(True)

    def count_click(self):
        self.clicks += 1
        self.click_button.setText(f"Click me ({self.clicks})")

    def closeEvent(self, event):
        # закриття посеред роботи: чекаємо на потік, щоб не отримати
        # "QThread: Destroyed while thread is still running"
        if self.thread is not None and self.thread.isRunning():
            # quit() зупиняє лише цикл подій потоку, а не run(), тому спершу
            # просимо воркер перервати роботу - він перевіряє це на кожному кроці
            self.thread.requestInterruption()
            self.thread.quit()
            self.thread.wait(3000)

        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)

    window = TaskWindow()
    window.resize(360, 180)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
