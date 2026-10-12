# Головне вікно: меню, панель інструментів, док зі списком, редактор, рядок стану.
#
# Таких вікон може бути кілька на один стан. Логіки нотаток тут немає:
# вікно перекладає дії користувача у виклики AppState, а інші вікна
# відкриває лише через WindowManager.

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QToolButton,
)

from .. import config
from ..state import FILTER_ALL, FILTER_OTHER, FILTER_PINNED, NO_SELECTION
from .note_editor_panel import NoteEditorPanel
from .note_list_panel import NoteListPanel

FILTER_TITLES = {FILTER_ALL: "All", FILTER_PINNED: "Pinned", FILTER_OTHER: "Other"}


class MainWindow(QMainWindow):
    closed = Signal()

    def __init__(self, state, windows, number):
        super().__init__()

        self.state = state
        self.windows = windows        # WindowManager: тільки він відкриває вікна
        self.number = number          # номер вікна: 1, 2, 3, ...

        self._build_ui()
        self._build_actions()
        self._build_menu()
        self._build_toolbar()
        self._connect()

        self.render_title()
        self.render_status()
        self.render_actions()

    # --- побудова -----------------------------------------------------------

    def _build_ui(self):
        self.list_panel = NoteListPanel(self.state)
        self.editor_panel = NoteEditorPanel(self.state)
        self.setCentralWidget(self.editor_panel)

        self.notes_dock = QDockWidget("Notes", self)
        self.notes_dock.setObjectName("notes_dock")
        self.notes_dock.setWidget(self.list_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.notes_dock)

        self.window_label = QLabel(f"Window: {self.number}")
        self.filter_label = QLabel()
        self.count_label = QLabel()
        self.statusBar().addPermanentWidget(self.window_label)
        self.statusBar().addPermanentWidget(self.filter_label)
        self.statusBar().addPermanentWidget(self.count_label)
        self.statusBar().showMessage("Ready")

    def _action(self, text, shortcut, slot):
        action = QAction(text, self)
        if shortcut is not None:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        return action

    def _build_actions(self):
        # кожна команда - один QAction з одним обробником; у меню й на панелі - той самий об'єкт
        self.new_action = self._action("&New note", QKeySequence.StandardKey.New, self.on_new_note)
        self.save_action = self._action("&Save note", QKeySequence.StandardKey.Save, self.on_save)
        self.delete_action = self._action("&Delete note", QKeySequence.StandardKey.Delete, self.on_delete)
        self.clear_action = self._action("&Clear all notes", None, self.on_clear_all)
        self.about_action = self._action("&About", None, self.on_about)

        self.open_action = self._action("&Open in new window", "Ctrl+Return", self.on_open_in_window)
        self.preferences_action = self._action("&Preferences...", "Ctrl+,", self.on_preferences)
        self.new_window_action = self._action(
            "&New window", "Ctrl+Shift+N", self.windows.open_main_window
        )
        self.close_window_action = self._action("&Close window", "Ctrl+W", self.close)
        # closeAllWindows, а не quit(): кожне вікно отримає closeEvent
        self.quit_action = self._action(
            "&Quit", QKeySequence.StandardKey.Quit, QApplication.closeAllWindows
        )

        # Delete має видаляти нотатку лише у списку, а не символ у редакторі
        self.delete_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.list_panel.addAction(self.delete_action)

        self.pin_action = QAction("&Pin", self)
        self.pin_action.setShortcut(QKeySequence("Ctrl+P"))
        self.pin_action.setCheckable(True)
        self.pin_action.triggered.connect(self.on_pin)

        self.export_txt_action = self._action("Export as &TXT...", None, lambda: self.on_export("txt"))
        self.export_csv_action = self._action("Export as &CSV...", None, lambda: self.on_export("csv"))

        # фільтр - група взаємовиключних перемикачів
        self.filter_group = QActionGroup(self)
        self.filter_actions = {}
        for name, title in FILTER_TITLES.items():
            action = QAction(title, self)
            action.setCheckable(True)
            action.triggered.connect(lambda checked=False, n=name: self.state.set_filter(n))
            self.filter_group.addAction(action)
            self.filter_actions[name] = action

    def _build_menu(self):
        note_menu = self.menuBar().addMenu("&Note")
        note_menu.addAction(self.new_action)
        note_menu.addAction(self.save_action)
        note_menu.addAction(self.delete_action)
        note_menu.addSeparator()
        note_menu.addAction(self.open_action)
        note_menu.addSeparator()
        export_menu = note_menu.addMenu("&Export")
        export_menu.addAction(self.export_txt_action)
        export_menu.addAction(self.export_csv_action)
        note_menu.addSeparator()
        note_menu.addAction(self.quit_action)

        edit_menu = self.menuBar().addMenu("&Edit")
        edit_menu.addAction(self.pin_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.clear_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.preferences_action)

        self.view_menu = self.menuBar().addMenu("&View")
        for action in self.filter_actions.values():
            self.view_menu.addAction(action)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.notes_dock.toggleViewAction())

        window_menu = self.menuBar().addMenu("&Window")
        window_menu.addAction(self.new_window_action)
        window_menu.addAction(self.close_window_action)

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(self.about_action)

    def _build_toolbar(self):
        self.main_toolbar = self.addToolBar("Main")
        self.main_toolbar.setObjectName("main_toolbar")
        self.main_toolbar.addAction(self.new_action)
        self.main_toolbar.addAction(self.save_action)
        self.main_toolbar.addAction(self.delete_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.open_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.pin_action)
        self.main_toolbar.addSeparator()
        for action in self.filter_actions.values():
            self.main_toolbar.addAction(action)
        self.main_toolbar.addSeparator()

        # Export - кнопка з випадаючим меню, а не звичайна кнопка
        export_menu = QMenu(self)
        export_menu.addAction(self.export_txt_action)
        export_menu.addAction(self.export_csv_action)
        export_button = QToolButton()
        export_button.setText("Export")
        export_button.setMenu(export_menu)
        export_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.main_toolbar.addWidget(export_button)

        self.main_toolbar.toggleViewAction().setText("&Toolbar")
        self.view_menu.addAction(self.main_toolbar.toggleViewAction())

    def _connect(self):
        self.list_panel.open_requested.connect(self.windows.open_note)

        self.state.notes_changed.connect(self.render_status)
        self.state.notes_changed.connect(self.render_actions)
        self.state.selection_changed.connect(self.render_actions)
        self.state.note_updated.connect(self.render_actions)
        self.state.dirty_changed.connect(self.render_title)
        self.state.filter_changed.connect(self.render_status)
        # помилки стану показує WindowManager - один раз, а не в кожному вікні

    # --- рендер -------------------------------------------------------------

    def render_title(self, dirty=None):
        number = "" if self.number == 1 else f" ({self.number})"
        mark = "*" if self.state.is_dirty() else ""
        self.setWindowTitle(f"{config.APP_TITLE}{number}{mark} - {config.AUTHOR}")
        self.save_action.setEnabled(self.state.is_dirty())

    def render_status(self, *args):
        current = self.state.current_filter()
        self.filter_actions[current].setChecked(True)
        self.filter_label.setText(f"Filter: {FILTER_TITLES[current]}")
        self.count_label.setText(f"Notes: {self.state.count()}")

    def render_actions(self, *args):
        note = self.state.selected_note()
        has_note = note is not None

        self.delete_action.setEnabled(has_note)
        self.pin_action.setEnabled(has_note)
        self.open_action.setEnabled(has_note)
        self.pin_action.setChecked(has_note and note.pinned)
        self.clear_action.setEnabled(self.state.count() > 0)

    # --- дії ----------------------------------------------------------------

    def on_new_note(self):
        self.state.add_note()
        self.editor_panel.text_edit.setFocus()
        self.statusBar().showMessage("New note - start typing", 3000)

    def on_save(self):
        if self.state.save():
            self.statusBar().showMessage("Saved", 3000)

    def on_delete(self):
        note = self.state.selected_note()
        if note is None:
            return

        answer = QMessageBox.question(
            self,
            config.APP_TITLE,
            f'Delete note {note.id} "{note.preview(config.DEFAULT_PREVIEW_LENGTH)}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            # вікно нотатки закриється само: менеджер підписаний на note_removed
            self.state.delete_note(note.id)
            self.statusBar().showMessage("Note deleted", 3000)

    def on_pin(self, checked):
        note_id = self.state.selected_id()
        if note_id != NO_SELECTION:
            self.state.set_pinned(note_id, checked)

    def on_open_in_window(self):
        note_id = self.state.selected_id()
        if note_id != NO_SELECTION:
            self.windows.open_note(note_id)

    def on_preferences(self):
        self.windows.open_preferences(self)

    def on_clear_all(self):
        answer = QMessageBox.question(
            self,
            config.APP_TITLE,
            f"Delete all {self.state.count()} notes? This cannot be undone after saving.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.state.clear_all()

    def on_export(self, fmt):
        if self.state.count() == 0:
            self.statusBar().showMessage("There is nothing to export", 3000)
            return

        file_filter = "CSV files (*.csv)" if fmt == "csv" else "Text files (*.txt)"
        path, _filter = QFileDialog.getSaveFileName(
            self, "Export notes", f"notes_export.{fmt}", file_filter
        )
        if not path:
            return

        header = f"{config.APP_TITLE} export - {config.AUTHOR}"
        if self.state.export(path, header):
            self.statusBar().showMessage(f"Exported to {Path(path).name}", 5000)

    def on_about(self):
        QMessageBox.about(
            self,
            f"About {config.APP_TITLE}",
            f"{config.APP_TITLE}\n{config.AUTHOR}\n\nDatabase: {config.DB_FILE}",
        )

    # --- закриття -----------------------------------------------------------

    def closeEvent(self, event):
        # про збереження питаємо лише при закритті останнього головного вікна
        if self.windows.is_last_main_window(self) and self.state.is_dirty():
            if not self._ask_save():
                event.ignore()
                return

        self.closed.emit()
        super().closeEvent(event)

    def _ask_save(self):
        # True - можна закриватись, False - лишитись.
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
            return False
        if answer == QMessageBox.StandardButton.Discard:
            return True
        return self.state.save()      # збереження не вдалося - не закриваємось
