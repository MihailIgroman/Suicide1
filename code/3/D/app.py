import sqlite3
import sys
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

STUDENT_NAME = "Andrii Dzhus"
STUDENT_GROUP = "IT-41"
DB_FILE = "workspace_andrii_dzhus.db"


class WorkspacePanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"Workspace - {STUDENT_NAME}")
        self.resize(600, 400)

        # Ініціалізація бази даних
        self.connection = sqlite3.connect(DB_FILE)
        self.init_db()

        # Елементи керування
        self.title_label = QLabel(f"{STUDENT_NAME}, {STUDENT_GROUP}")
        self.counter_label = QLabel("Notes: 0")

        self.add_button = QPushButton("Add")
        self.delete_button = QPushButton("Delete last")
        self.clear_button = QPushButton("Clear all")

        self.note_field = QLineEdit()
        self.note_field.setPlaceholderText("Enter a new note here...")

        self.preview_label = QLabel("No notes yet")
        self.preview_label.setStyleSheet("background-color: #ffffff; color: #000000; border: 1px solid #cccccc; padding: 8px;")
        self.preview_label.setWordWrap(True)

        self.status_label = QLabel(f"Database: {DB_FILE}")
        self.quit_button = QPushButton("Quit")

        # Компонування
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.counter_label)

        left_buttons_layout = QVBoxLayout()
        left_buttons_layout.addWidget(self.add_button)
        left_buttons_layout.addWidget(self.delete_button)
        left_buttons_layout.addWidget(self.clear_button)
        left_buttons_layout.addStretch()

        right_content_layout = QVBoxLayout()
        right_content_layout.addWidget(self.note_field)
        right_content_layout.addWidget(self.preview_label, stretch=1)

        middle_layout = QHBoxLayout()
        middle_layout.addLayout(left_buttons_layout)
        middle_layout.addLayout(right_content_layout, stretch=1)

        footer_layout = QHBoxLayout()
        footer_layout.addWidget(self.status_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.quit_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addLayout(middle_layout, stretch=1)
        main_layout.addLayout(footer_layout)
        self.setLayout(main_layout)

        # З'єднання сигналів зі слотами
        self.add_button.clicked.connect(self.on_add)
        self.delete_button.clicked.connect(self.on_delete)
        self.clear_button.clicked.connect(self.on_clear)
        self.quit_button.clicked.connect(self.close)

        self.refresh()

    def init_db(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        self.connection.commit()

    def refresh(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT created_at, text FROM notes ORDER BY id")
        rows = cursor.fetchall()

        if rows:
            lines = [f"{row[0]}  {row[1]}" for row in rows]
            self.preview_label.setText("\n".join(lines))
        else:
            self.preview_label.setText("No notes yet")

        self.counter_label.setText(f"Notes: {len(rows)}")

    def on_add(self):
        text = self.note_field.text().strip()
        if not text:
            return

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO notes (text, created_at) VALUES (?, ?)", (text, created_at))
        self.connection.commit()

        self.note_field.clear()
        self.refresh()

    def on_delete(self):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM notes WHERE id = (SELECT MAX(id) FROM notes)")
        self.connection.commit()
        self.refresh()

    def on_clear(self):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM notes")
        self.connection.commit()
        self.refresh()

    def closeEvent(self, event):
        self.connection.close()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = WorkspacePanel()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()