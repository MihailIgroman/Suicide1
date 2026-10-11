import sys
from pathlib import Path

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QTextEdit,
)

STUDENT_NAME = "Andrii Dzhus"
STUDENT_GROUP = "IT-41"


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_path = None
        self.is_modified = False

        self.editor = QTextEdit()
        self.editor.textChanged.connect(self.on_text_changed)
        self.setCentralWidget(self.editor)

        self.chars_label = QLabel("Chars: 0")
        self.statusBar().addPermanentWidget(self.chars_label)
        self.statusBar().showMessage("Ready")

        self.create_actions()
        self.create_menus()

        self.update_title()

    def create_actions(self):
        self.new_action = QAction("New", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.triggered.connect(self.on_new)

        self.open_action = QAction("Open...", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.on_open)

        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.on_save)

        self.save_as_action = QAction("Save As...", self)
        self.save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.save_as_action.triggered.connect(self.on_save_as)

        self.quit_action = QAction("Quit", self)
        self.quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.quit_action.triggered.connect(self.close)

        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.on_about)

    def create_menus(self):
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction(self.about_action)

    def update_title(self):
        file_name = self.current_path.name if self.current_path else "Untitled"
        mark = "*" if self.is_modified else ""
        self.setWindowTitle(f"{file_name}{mark} - Text Editor - {STUDENT_NAME}, {STUDENT_GROUP}")

    def on_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            self.update_title()

        text_length = len(self.editor.toPlainText())
        self.chars_label.setText(f"Chars: {text_length}")

    def confirm_discard(self):
        if not self.is_modified:
            return True

        answer = QMessageBox.warning(
            self,
            "Unsaved changes",
            "The document has unsaved changes. Do you want to save them?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

        if answer == QMessageBox.StandardButton.Save:
            return self.on_save()
        elif answer == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def on_new(self):
        if not self.confirm_discard():
            return

        self.editor.clear()
        self.current_path = None
        self.is_modified = False
        self.update_title()
        self.statusBar().showMessage("New file", 2000)

    def on_open(self):
        if not self.confirm_discard():
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Text files (*.txt);;All files (*)"
        )
        if not path:
            return

        try:
            content = Path(path).read_text(encoding="utf-8")
            self.editor.setPlainText(content)
            self.current_path = Path(path)
            self.is_modified = False
            self.update_title()
            self.statusBar().showMessage(f"Opened: {path}", 2000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read file:\n{e}")

    def on_save(self):
        if self.current_path is None:
            return self.on_save_as()

        try:
            self.current_path.write_text(self.editor.toPlainText(), encoding="utf-8")
            self.is_modified = False
            self.update_title()
            self.statusBar().showMessage("Saved successfully", 2000)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
            return False

    def on_save_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "untitled.txt", "Text files (*.txt);;All files (*)"
        )
        if not path:
            return False

        self.current_path = Path(path)
        return self.on_save()

    def on_about(self):
        QMessageBox.about(
            self,
            "About Text Editor",
            f"Simple Text Editor\nStudent: {STUDENT_NAME}\nGroup: {STUDENT_GROUP}",
        )

    def closeEvent(self, event):
        if self.confirm_discard():
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    window = TextEditor()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()