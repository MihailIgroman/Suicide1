import sqlite3
import sys
from datetime import datetime

from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QTextEdit,
)

STUDENT_NAME = "Andrii Zelyuk"
STUDENT_GROUP = "IT-41"
DB_FILE = "workspace_andrii_zelyuk.db"
SETTINGS_APP = "NotesAppAndriiZelyuk"


class NotesWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"Notes - {STUDENT_NAME}, {STUDENT_GROUP}")

        self.connection = sqlite3.connect(DB_FILE)
        self.init_db()

        self.current_note_id = None

        self.note_editor = QTextEdit()
        self.setCentralWidget(self.note_editor)

        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.on_note_selected)

        self.notes_dock = QDockWidget("Notes List", self)
        self.notes_dock.setObjectName("notes_dock")
        self.notes_dock.setWidget(self.notes_list)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.notes_dock)

        self.create_actions()

        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.delete_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        view_menu = self.menuBar().addMenu("View")
        view_menu.addAction(self.notes_dock.toggleViewAction())

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction(self.about_action)

        self.main_toolbar = self.addToolBar("Main Toolbar")
        self.main_toolbar.setObjectName("main_toolbar")
        self.main_toolbar.addAction(self.new_action)
        self.main_toolbar.addAction(self.save_action)
        self.main_toolbar.addAction(self.delete_action)

        self.counter_label = QLabel("Notes: 0")
        self.statusBar().addPermanentWidget(self.counter_label)
        self.statusBar().showMessage("Ready")

        self.settings = QSettings("KTBP", SETTINGS_APP)
        self.restore_settings()

        self.refresh_notes()

    def create_actions(self):
        self.new_action = QAction("New", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.triggered.connect(self.on_new)

        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.on_save)

        self.delete_action = QAction("Delete", self)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.triggered.connect(self.on_delete)

        self.quit_action = QAction("Quit", self)
        self.quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.quit_action.triggered.connect(self.close)

        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.on_about)

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

    def refresh_notes(self):
        self.notes_list.clear()
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, text, created_at FROM notes ORDER BY id DESC")
        rows = cursor.fetchall()

        for note_id, text, created_at in rows:
            preview = text.split("\n")[0][:25]
            item = QListWidgetItem(f"{created_at} - {preview}")
            item.setData(Qt.ItemDataRole.UserRole, note_id)
            self.notes_list.addItem(item)

        self.counter_label.setText(f"Notes: {len(rows)}")

    def on_note_selected(self, item):
        self.current_note_id = item.data(Qt.ItemDataRole.UserRole)
        cursor = self.connection.cursor()
        cursor.execute("SELECT text FROM notes WHERE id = ?", (self.current_note_id,))
        row = cursor.fetchone()
        if row:
            self.note_editor.setPlainText(row[0])

    def on_new(self):
        self.current_note_id = None
        self.note_editor.clear()
        self.notes_list.clearSelection()
        self.statusBar().showMessage("New note draft created", 2000)

    def on_save(self):
        text = self.note_editor.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Cannot save empty note.")
            return

        cursor = self.connection.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

        if self.current_note_id is None:
            cursor.execute("INSERT INTO notes (text, created_at) VALUES (?, ?)", (text, created_at))
            self.current_note_id = cursor.lastrowid
            self.statusBar().showMessage("Note created", 2000)
        else:
            cursor.execute("UPDATE notes SET text = ? WHERE id = ?", (text, self.current_note_id))
            self.statusBar().showMessage("Note updated", 2000)

        self.connection.commit()
        self.refresh_notes()

    def on_delete(self):
        if self.current_note_id is None:
            return

        answer = QMessageBox.question(self, "Delete", "Delete selected note?")
        if answer == QMessageBox.StandardButton.Yes:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (self.current_note_id,))
            self.connection.commit()
            self.on_new()
            self.refresh_notes()

    def on_about(self):
        QMessageBox.about(self, "About", f"Notes App\nStudent: {STUDENT_NAME}\nGroup: {STUDENT_GROUP}")

    def restore_settings(self):
        geometry = self.settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

        state = self.settings.value("window_state")
        if state is not None:
            self.restoreState(state)

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())
        self.connection.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = NotesWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()