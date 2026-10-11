import csv
import sqlite3
import sys
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTextEdit,
    QToolButton,
)

STUDENT_NAME = "Andrii Zelyuk"
STUDENT_GROUP = "IT-41"
DB_FILE = "workspace_andrii_zelyuk.db"


class NotesManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"Notes Manager - {STUDENT_NAME}, {STUDENT_GROUP}")

        self.connection = sqlite3.connect(DB_FILE)
        self.init_db()

        self.current_note_id = None
        self.current_filter = "All"

        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)

        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.on_note_selected)
        self.notes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notes_list.customContextMenuRequested.connect(self.show_context_menu)

        self.notes_dock = QDockWidget("Notes", self)
        self.notes_dock.setObjectName("notes_dock")
        self.notes_dock.setWidget(self.notes_list)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.notes_dock)

        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        self.create_statusbar()

        self.refresh()

    def init_db(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                pinned INTEGER NOT NULL DEFAULT 0
            )
        """)
        cursor.execute("PRAGMA table_info(notes)")
        columns = [column[1] for column in cursor.fetchall()]
        if "pinned" not in columns:
            cursor.execute("ALTER TABLE notes ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0")
        self.connection.commit()

    def create_actions(self):
        self.new_action = QAction("New note", self)
        self.new_action.setShortcut(QKeySequence("Ctrl+N"))
        self.new_action.triggered.connect(self.on_new)

        self.save_action = QAction("Save note", self)
        self.save_action.setShortcut(QKeySequence("Ctrl+S"))
        self.save_action.triggered.connect(self.on_save)

        self.delete_action = QAction("Delete note", self)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.triggered.connect(self.on_delete)

        self.pin_action = QAction("Pin / Unpin", self)
        self.pin_action.setShortcut(QKeySequence("Ctrl+P"))
        self.pin_action.setCheckable(True)
        self.pin_action.triggered.connect(self.on_toggle_pin)

        self.clear_all_action = QAction("Clear all notes", self)
        self.clear_all_action.triggered.connect(self.on_clear_all)

        self.quit_action = QAction("Quit", self)
        self.quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.quit_action.triggered.connect(self.close)

        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.on_about)

        self.export_txt_action = QAction("Export to TXT", self)
        self.export_txt_action.triggered.connect(self.on_export_txt)

        self.export_csv_action = QAction("Export to CSV", self)
        self.export_csv_action.triggered.connect(self.on_export_csv)

        self.filter_group = QActionGroup(self)
        self.filter_group.setExclusive(True)

        self.filter_all = QAction("All", self)
        self.filter_all.setCheckable(True)
        self.filter_all.setChecked(True)
        self.filter_all.setData("All")

        self.filter_pinned = QAction("Pinned", self)
        self.filter_pinned.setCheckable(True)
        self.filter_pinned.setData("Pinned")

        self.filter_other = QAction("Other", self)
        self.filter_other.setCheckable(True)
        self.filter_other.setData("Other")

        for act in (self.filter_all, self.filter_pinned, self.filter_other):
            self.filter_group.addAction(act)

        self.filter_group.triggered.connect(self.on_filter_changed)

    def create_menus(self):
        menu_bar = self.menuBar()

        note_menu = menu_bar.addMenu("Note")
        note_menu.addAction(self.new_action)
        note_menu.addAction(self.save_action)
        note_menu.addAction(self.delete_action)
        note_menu.addSeparator()
        note_menu.addAction(self.pin_action)
        note_menu.addSeparator()
        export_menu = note_menu.addMenu("Export")
        export_menu.addAction(self.export_txt_action)
        export_menu.addAction(self.export_csv_action)
        note_menu.addSeparator()
        note_menu.addAction(self.quit_action)

        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self.clear_all_action)

        view_menu = menu_bar.addMenu("View")
        view_menu.addAction(self.notes_dock.toggleViewAction())
        view_menu.addSeparator()
        for act in self.filter_group.actions():
            view_menu.addAction(act)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self.about_action)

    def create_toolbar(self):
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.delete_action)
        toolbar.addSeparator()
        toolbar.addAction(self.pin_action)
        toolbar.addSeparator()

        for act in self.filter_group.actions():
            toolbar.addAction(act)

        toolbar.addSeparator()

        export_menu = QMenu(self)
        export_menu.addAction(self.export_txt_action)
        export_menu.addAction(self.export_csv_action)

        export_btn = QToolButton()
        export_btn.setText("Export")
        export_btn.setMenu(export_menu)
        export_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar.addWidget(export_btn)

    def create_statusbar(self):
        self.filter_label = QLabel("Filter: All")
        self.counter_label = QLabel("Notes: 0")

        self.statusBar().addPermanentWidget(self.filter_label)
        self.statusBar().addPermanentWidget(self.counter_label)
        self.statusBar().showMessage("Ready")

    def refresh(self):
        self.notes_list.clear()
        cursor = self.connection.cursor()

        query = "SELECT id, text, created_at, pinned FROM notes "
        if self.current_filter == "Pinned":
            query += "WHERE pinned = 1 "
        elif self.current_filter == "Other":
            query += "WHERE pinned = 0 "
        query += "ORDER BY pinned DESC, id DESC"

        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM notes")
        total_count = cursor.fetchone()[0]

        for note_id, text, created_at, pinned in rows:
            mark = "[P] " if pinned else ""
            preview = text.split("\n")[0][:20]
            item = QListWidgetItem(f"{mark}{created_at} - {preview}")
            item.setData(Qt.ItemDataRole.UserRole, note_id)
            self.notes_list.addItem(item)

        self.counter_label.setText(f"Notes: {total_count}")
        self.filter_label.setText(f"Filter: {self.current_filter}")
        self.update_actions()

    def update_actions(self):
        has_selection = self.current_note_id is not None
        self.delete_action.setEnabled(has_selection)
        self.pin_action.setEnabled(has_selection)

        if has_selection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT pinned FROM notes WHERE id = ?", (self.current_note_id,))
            row = cursor.fetchone()
            if row:
                self.pin_action.setChecked(bool(row[0]))

    def on_note_selected(self, item):
        self.current_note_id = item.data(Qt.ItemDataRole.UserRole)
        cursor = self.connection.cursor()
        cursor.execute("SELECT text FROM notes WHERE id = ?", (self.current_note_id,))
        row = cursor.fetchone()
        if row:
            self.editor.setPlainText(row[0])
        self.update_actions()

    def show_context_menu(self, pos):
        item = self.notes_list.itemAt(pos)
        if item:
            self.on_note_selected(item)
            menu = QMenu(self)
            menu.addAction(self.save_action)
            menu.addAction(self.pin_action)
            menu.addAction(self.delete_action)
            menu.exec(self.notes_list.mapToGlobal(pos))

    def on_new(self):
        self.current_note_id = None
        self.editor.clear()
        self.notes_list.clearSelection()
        self.update_actions()
        self.statusBar().showMessage("New draft created", 2000)

    def on_save(self):
        text = self.editor.toPlainText().strip()
        if not text:
            return

        cursor = self.connection.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

        if self.current_note_id is None:
            cursor.execute("INSERT INTO notes (text, created_at, pinned) VALUES (?, ?, 0)", (text, created_at))
            self.current_note_id = cursor.lastrowid
        else:
            cursor.execute("UPDATE notes SET text = ? WHERE id = ?", (text, self.current_note_id))

        self.connection.commit()
        self.refresh()
        self.statusBar().showMessage("Note saved", 2000)

    def on_delete(self):
        if self.current_note_id is None:
            return

        answer = QMessageBox.question(self, "Delete", "Delete this note?")
        if answer == QMessageBox.StandardButton.Yes:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (self.current_note_id,))
            self.connection.commit()
            self.on_new()
            self.refresh()

    def on_toggle_pin(self):
        if self.current_note_id is None:
            return

        new_pinned = 1 if self.pin_action.isChecked() else 0
        cursor = self.connection.cursor()
        cursor.execute("UPDATE notes SET pinned = ? WHERE id = ?", (new_pinned, self.current_note_id))
        self.connection.commit()
        self.refresh()

    def on_clear_all(self):
        answer = QMessageBox.question(self, "Clear All", "Delete ALL notes permanently?")
        if answer == QMessageBox.StandardButton.Yes:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM notes")
            self.connection.commit()
            self.on_new()
            self.refresh()

    def on_filter_changed(self, action):
        self.current_filter = action.data()
        self.refresh()

    def on_export_txt(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export to TXT", "all_notes.txt", "Text Files (*.txt)")
        if not path:
            return

        cursor = self.connection.cursor()
        cursor.execute("SELECT created_at, text FROM notes ORDER BY id DESC")
        rows = cursor.fetchall()

        with open(path, "w", encoding="utf-8") as f:
            for created_at, text in rows:
                f.write(f"=== {created_at} ===\n{text}\n\n")

        self.statusBar().showMessage("Exported to TXT", 2000)

    def on_export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "all_notes.csv", "CSV Files (*.csv)")
        if not path:
            return

        cursor = self.connection.cursor()
        cursor.execute("SELECT id, created_at, pinned, text FROM notes ORDER BY id DESC")
        rows = cursor.fetchall()

        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "created_at", "pinned", "text"])
            writer.writerows(rows)

        self.statusBar().showMessage("Exported to CSV", 2000)

    def on_about(self):
        QMessageBox.about(self, "About", f"Notes Manager\nStudent: {STUDENT_NAME}\nGroup: {STUDENT_GROUP}")

    def closeEvent(self, event):
        self.connection.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = NotesManager()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()