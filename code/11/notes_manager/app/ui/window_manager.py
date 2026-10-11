"""Реєстр відкритих вікон. Єдине місце, яке знає, які вікна відкриті.

Тут же живуть речі рівня застосунку, яких не має бути по копії
на кожне вікно: таймер автозбереження та показ помилок стану.
"""

import logging

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from .. import config, settings as settings_module
from .main_window import MainWindow
from .note_window import NoteWindow
from .preferences_dialog import PreferencesDialog

logger = logging.getLogger(__name__)


class WindowManager:
    def __init__(self, state, settings, log_path):
        self.state = state
        self.settings = settings
        self.log_path = log_path

        self._main_windows = []           # головні вікна в порядку відкриття
        self._note_windows = {}           # note_id -> NoteWindow
        self._next_number = 1

        self._autosave_timer = QTimer()
        self._autosave_timer.timeout.connect(self.on_autosave)

        self.state.note_removed.connect(self.close_note)
        # одна помилка - одне повідомлення, хоч би скільки вікон було відкрито
        self.state.error_occurred.connect(self.show_error)
        self.settings.changed.connect(self.apply_settings)

        self.apply_settings()

    # --- відкриття ----------------------------------------------------------

    def open_main_window(self):
        number = self._next_number
        self._next_number += 1

        window = MainWindow(self.state, self.settings, self, number, self.log_path)
        window.closed.connect(lambda: self.forget_main_window(window))

        if not self._main_windows:
            window.restore_layout()                   # перше вікно - як минулого разу
        else:
            last = self._main_windows[-1]
            window.resize(last.size())
            window.move(last.x() + config.CASCADE_STEP, last.y() + config.CASCADE_STEP)

        self._main_windows.append(window)
        window.show()
        logger.info("Main window %s opened", number)
        return window

    def open_note(self, note_id):
        if self.state.find(note_id) is None:
            return None

        window = self._note_windows.get(note_id)
        if window is None:
            window = NoteWindow(self.state, note_id)
            window.closed.connect(self.forget_note_window)
            window.set_font_size(self.settings.font_size)
            window.resize(460, 360)
            self._note_windows[note_id] = window

        # повторне відкриття не створює копію, а піднімає наявне вікно
        window.show()
        window.raise_()
        window.activateWindow()
        return window

    def open_preferences(self, parent):
        values = self.settings.values()
        values["pinned_first"] = self.state.pinned_first()

        limits = {
            "preview_length": (settings_module.PREVIEW_MIN, settings_module.PREVIEW_MAX),
            "font_size": (settings_module.FONT_SIZE_MIN, settings_module.FONT_SIZE_MAX),
            "autosave_interval_s": (settings_module.INTERVAL_MIN, settings_module.INTERVAL_MAX),
            "log_level": settings_module.LOG_LEVELS,
        }

        dialog = PreferencesDialog(values, limits, parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False

        new_values = dialog.values()
        self.state.set_pinned_first(new_values.pop("pinned_first"))
        self.settings.apply(new_values)
        return True

    # --- закриття -----------------------------------------------------------

    def is_last_main_window(self, window):
        return self._main_windows == [window]

    def close_note(self, note_id):
        window = self._note_windows.get(note_id)
        if window is not None:
            window.close()

    def close_all_notes(self):
        # list(...): close() видаляє запис зі словника під час обходу
        for window in list(self._note_windows.values()):
            window.close()

    def forget_note_window(self, note_id):
        self._note_windows.pop(note_id, None)

    def forget_main_window(self, window):
        if window in self._main_windows:
            self._main_windows.remove(window)
            logger.info("Main window %s closed", window.number)

        # закрилось останнє головне вікно - допоміжним нема біля чого жити
        if not self._main_windows:
            self.close_all_notes()
            self._autosave_timer.stop()

    # --- налаштування й автозбереження ----------------------------------------

    def apply_settings(self):
        for window in self._note_windows.values():
            window.set_font_size(self.settings.font_size)

        if self.settings.autosave:
            self._autosave_timer.start(self.settings.autosave_interval_s * 1000)
        else:
            self._autosave_timer.stop()

        logger.debug(
            "Autosave: %s, every %s s",
            self.settings.autosave,
            self.settings.autosave_interval_s,
        )

    def on_autosave(self):
        if not self.state.is_dirty():
            return

        logger.debug("Autosave tick")
        if self.state.save():
            for window in self._main_windows:
                window.statusBar().showMessage("Saved automatically", 3000)
            return

        # не смикаємо недоступний диск кожні N секунд: вимикаємо таймер
        self._autosave_timer.stop()
        logger.warning("Autosave stopped after a failure")
        for window in self._main_windows:
            window.message_bar.show_message(
                "Autosave is turned off after a failure. "
                "Fix the problem and save manually (Ctrl+S)."
            )

    # --- помилки ------------------------------------------------------------

    def show_error(self, message):
        parent = QApplication.activeWindow()
        if parent is None and self._main_windows:
            parent = self._main_windows[-1]

        where = self.log_path if self.log_path is not None else "the console"

        box = QMessageBox(parent)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(config.APP_TITLE)
        box.setText(message)
        box.setInformativeText("Your notes are still open. Nothing is lost yet.")
        box.setDetailedText(f"Technical details are in the log file:\n{where}")
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()
