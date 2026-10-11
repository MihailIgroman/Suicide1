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

        self.setWindowTitle("Business Card - Andrii Zelyuk")
        self.setFixedSize(320, 200)

        self.name_label = QLabel("Andrii Zelyuk")
        self.group_label = QLabel("Group: IT-41")
        self.course_label = QLabel("Python Programming, Semester 3")

        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.course_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

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