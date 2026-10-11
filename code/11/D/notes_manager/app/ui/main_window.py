"""Головне вікно: меню, панель інструментів, док зі списком, редактор, рядок стану.

Таких вікон може бути кілька на один стан. Вікно нічого не створює саме:
стан, налаштування й менеджер вікон отримує в конструкторі.
"""

import logging
from pathlib import Path

from PySide6.QtCore import QStandardPaths, Qt, QUrl, Signal
from PySide6.QtGui import QAction, QDesktopServices, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from .. import config
from ..state import NO_SELECTION
from .message_bar import MessageBar
from .note_editor_panel import NoteEditorPanel
from .note_list_panel import NoteListPanel

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    closed = Signal()

    def __init__(self, state, settings, windows, number, log_path):
        super().__init__()

        self.state = state
        self.settings = settings
        self.windows = windows        # WindowManager: тільки він відкриває вікна
        self.number = number
        self.log_path = log_path

        self._build_ui()
        self._build_actions()
        self._build_menu()
        self._build_toolbar()
        self._connect()

        self.apply_settings()
        self.render_title()
        self.render_status()
        self.render_actions()

    # --- побудова -----------------------------------------------------------

    def _build_ui(self):
        self.message_bar = MessageBar()

        self.list_panel = NoteListPanel(self.state, self.settings.preview_length)
        self.editor_panel = NoteEditorPanel(self.state)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.message_bar)
        layout.addWidget(self.editor_panel, 1)
        self.setCentralWidget(central)

        # objectName обов'язковий, інакше saveState() не відновить док
        self.list_dock = QDockWidget("Notes", self)
        self.list_dock.setObjectName("notes_dock")
        self.list_dock.setWidget(self.list_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.list_dock)

        self.window_label = QLabel(f"Window: {self.number}")
        self.count_label = QLabel()
        self.statusBar().addPermanentWidget(self.window_label)
        self.statusBar().addPermanentWidget(self.count_label)
        self.statusBar().showMessage("Ready")

    def _action(self, text, shortcut, slot):
        action = QAction(text, self)
        if shortcut is not None:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        return action

    def _build_actions(self):
        self.new_action = self._action("&New note", QKeySequence.StandardKey.New, self.on_new_note)
        self.save_action = self._action("&Save note", QKeySequence.StandardKey.Save, self.on_save)
        self.delete_action = self._action("&Delete note", QKeySequence.StandardKey.Delete, self.on_delete)
        self.pin_action = self._action("&Pin / Unpin", "Ctrl+P", self.on_pin)
        self.open_action = self._action("&Open in new window", "Ctrl+Return", self.on_open_in_window)
        self.export_action = self._action("&Export...", "Ctrl+E", self.on_export)
        # closeAllWindows, а не quit(): кожне вікно отримає closeEvent
        self.quit_action = self._action("&Quit", QKeySequence.StandardKey.Quit, QApplication.closeAllWindows)

        self.preferences_action = self._action("&Preferences...", "Ctrl+,", self.on_preferences)

        self.new_window_action = self._action("&New window", "Ctrl+Shift+N", self.windows.open_main_window)
        self.close_window_action = self._action("&Close window", "Ctrl+W", self.close)
        self.reset_layout_action = self._action("&Reset window layout", None, self.on_reset_layout)

        self.about_action = self._action("&About", None, self.on_about)
        self.log_folder_action = self._action("Open &log folder", None, self.on_open_log_folder)
        self.test_error_action = self._action("Raise a test &error", None, self.on_test_error)

        # Delete має видаляти нотатку лише в таблиці, а не символ у редакторі
        self.delete_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.list_panel.addAction(self.delete_action)

    def _build_menu(self):
        note_menu = self.menuBar().addMenu("&Note")
        note_menu.addAction(self.new_action)
        note_menu.addAction(self.save_action)
        note_menu.addAction(self.delete_action)
        note_menu.addAction(self.pin_action)
        note_menu.addSeparator()
        note_menu.addAction(self.open_action)
        note_menu.addSeparator()
        note_menu.addAction(self.export_action)
        self.recent_menu = note_menu.addMenu("Recent e&xports")
        self.recent_menu.aboutToShow.connect(self.render_recent_exports)
        note_menu.addSeparator()
        note_menu.addAction(self.quit_action)

        edit_menu = self.menuBar().addMenu("&Edit")
        edit_menu.addAction(self.preferences_action)

        window_menu = self.menuBar().addMenu("&Window")
        window_menu.addAction(self.new_window_action)
        window_menu.addAction(self.close_window_action)
        window_menu.addSeparator()
        window_menu.addAction(self.reset_layout_action)

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(self.about_action)
        help_menu.addAction(self.log_folder_action)
        help_menu.addSeparator()
        help_menu.addAction(self.test_error_action)

    def _build_toolbar(self):
        toolbar = self.addToolBar("Main")
        toolbar.setObjectName("main_toolbar")
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.delete_action)
        toolbar.addSeparator()
        toolbar.addAction(self.open_action)

    def _connect(self):
        self.list_panel.open_requested.connect(self.windows.open_note)

        self.state.notes_changed.connect(self.render_status)
        self.state.selection_changed.connect(self.render_actions)
        self.state.note_updated.connect(self.render_actions)
        self.state.dirty_changed.connect(self.render_title)

        self.settings.changed.connect(self.apply_settings)

    # --- рендер -------------------------------------------------------------

    def render_title(self, dirty=None):
        number = "" if self.number == 1 else f" ({self.number})"
        mark = "*" if self.state.is_dirty() else ""
        self.setWindowTitle(f"{config.APP_TITLE}{number}{mark} - {config.AUTHOR}")
        self.save_action.setEnabled(self.state.is_dirty())

    def render_status(self):
        self.count_label.setText(f"Notes: {self.state.count()}")

    def render_actions(self, note_id=None):
        note = self.state.selected_note()
        has_note = note is not None

        self.delete_action.setEnabled(has_note)
        self.pin_action.setEnabled(has_note)
        self.open_action.setEnabled(has_note)
        self.pin_action.setText("Un&pin" if has_note and note.pinned else "&Pin")

    def render_recent_exports(self):
        self.recent_menu.clear()

        paths = self.settings.recent_exports()
        if not paths:
            empty = self.recent_menu.addAction("(no exports yet)")
            empty.setEnabled(False)
            return

        for path in paths:
            action = self.recent_menu.addAction(path)
            action.triggered.connect(lambda checked=False, p=path: self.on_open_recent(p))

        self.recent_menu.addSeparator()
        self.recent_menu.addAction("Clear list", self.settings.clear_recent_exports)

    def apply_settings(self):
        self.editor_panel.set_font_size(self.settings.font_size)
        self.list_panel.set_preview_length(self.settings.preview_length)

    # --- дії ----------------------------------------------------------------

    def on_new_note(self):
        self.state.add_note()
        self.editor_panel.text_edit.setFocus()

    def on_save(self):
        if self.state.save():
            self.statusBar().showMessage("Saved", 3000)

    def on_delete(self):
        note = self.state.selected_note()
        if note is None:
            self.message_bar.show_message("Select a note first.", 4000)
            return

        if self.settings.confirm_delete:
            answer = QMessageBox.question(
                self,
                config.APP_TITLE,
                f'Delete note {note.id} "{note.preview(config.DEFAULT_PREVIEW_LENGTH)}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        # вікно нотатки закриється само: менеджер підписаний на note_removed
        self.state.delete_note(note.id)
        self.statusBar().showMessage("Note deleted", 3000)

    def on_pin(self):
        note_id = self.state.selected_id()
        if note_id != NO_SELECTION:
            self.state.toggle_pinned(note_id)

    def on_open_in_window(self):
        note_id = self.state.selected_id()
        if note_id == NO_SELECTION:
            self.message_bar.show_message("Select a note first.", 4000)
            return
        self.windows.open_note(note_id)

    def on_export(self):
        if self.state.count() == 0:
            self.message_bar.show_message("There is nothing to export yet.", 4000)
            return

        documents = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        path, _filter = QFileDialog.getSaveFileName(
            self,
            "Export notes",
            str(Path(documents) / "notes_export.txt"),
            "Text files (*.txt);;All files (*)",
        )
        if not path:
            return

        header = f"{config.APP_TITLE} export - {config.AUTHOR}"
        if self.state.export(path, header):
            self.settings.add_recent_export(path)
            self.statusBar().showMessage(f"Exported to {path}", 5000)

    def on_open_recent(self, path):
        if not Path(path).exists():
            logger.warning("Recent export is missing: %s", path)
            self.message_bar.show_message(f"File not found: {path}", 6000)
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def on_preferences(self):
        if self.windows.open_preferences(self):
            self.statusBar().showMessage("Preferences saved", 3000)

    def on_reset_layout(self):
        self.settings.reset_window()
        QMessageBox.information(
            self, config.APP_TITLE, "Window layout will be reset on the next start."
        )

    def on_about(self):
        QMessageBox.about(
            self,
            f"About {config.APP_TITLE}",
            f"{config.APP_TITLE}\n{config.AUTHOR}\n\n"
            f"Settings: {self.settings.file_name()}\n"
            f"Log: {self.log_path if self.log_path else 'console only'}",
        )

    def on_open_log_folder(self):
        if self.log_path is None:
            self.message_bar.show_message("The log file is unavailable, see the console.", 6000)
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.log_path.parent)))

    def on_test_error(self):
        notes = {}
        return notes["no such key"]          # навмисний KeyError для перевірки хука

    # --- геометрія й закриття ------------------------------------------------

    def restore_layout(self):
        geometry = self.settings.window_geometry()
        if geometry.isEmpty() or not self.restoreGeometry(geometry):
            self.resize(900, 560)            # перший запуск або зіпсоване значення

        window_state = self.settings.window_state()
        if not window_state.isEmpty() and not self.restoreState(window_state):
            logger.warning("Saved window state could not be restored")

    def closeEvent(self, event):
        # питаємо про збереження лише при закритті останнього головного вікна
        if self.windows.is_last_main_window(self) and self.state.is_dirty():
            answer = QMessageBox.question(
                self,
                config.APP_TITLE,
                "There are unsaved changes. Save before closing?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )

            if answer == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return

            if answer == QMessageBox.StandardButton.Save and not self.state.save():
                event.ignore()               # збереження не вдалося - не закриваємось
                return

        self.settings.save_window(self.saveGeometry(), self.saveState())
        self.closed.emit()
        super().closeEvent(event)
