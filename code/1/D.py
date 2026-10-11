import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class BusinessCard(QWidget):
    def __init__(self):
        super().__init__()

        # Заголовок вікна з транслітерацією імені та прізвища
        self.setWindowTitle("Business Card - Andrii Dzhus")

        # Фіксований розмір вікна 320x200
        self.setFixedSize(320, 200)

        # Створення трьох міток QLabel
        self.name_label = QLabel("Andrii Dzhus")
        self.group_label = QLabel("Group: IT-41")
        self.course_label = QLabel("Python Programming, Semester 3")

        # Вирівнювання по центру та оформлення
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.course_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        # Кнопка для закриття вікна
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        # Розміщення віджетів у вертикальному компонувальнику
        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.group_label)
        layout.addWidget(self.course_label)
        layout.addStretch()
        layout.addWidget(self.close_button)

        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    window = BusinessCard()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()