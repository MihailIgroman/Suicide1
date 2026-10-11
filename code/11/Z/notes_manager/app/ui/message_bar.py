"""Ненав'язлива смужка з повідомленням над вмістом вікна."""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton


class MessageBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("MessageBar { background: #fdf0d5; border: 1px solid #d9a441; }")
        self.hide()

        self._label = QLabel()
        self._label.setWordWrap(True)
        self._label.setStyleSheet("color: #3a2a00;")

        close_button = QToolButton()
        close_button.setText("x")
        close_button.clicked.connect(self.hide)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 4, 4)
        layout.addWidget(self._label, 1)
        layout.addWidget(close_button)

    def show_message(self, text, timeout_ms=0):
        self._label.setText(text)
        self.show()

        self._timer.stop()
        if timeout_ms > 0:
            self._timer.start(timeout_ms)
