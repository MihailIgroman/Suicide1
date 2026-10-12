# Реєстр відкритих вікон. Єдине місце, яке знає, які вікна відкриті.
#
# Вікна одне про одного не знають: усі звертаються сюди.

from PySide6.QtWidgets import QApplication, QMessageBox

from .. import config
from .main_window import MainWindow
from .note_window import NoteWindow
from .preferences_dialog import PreferencesDialog


class WindowManager:
    def __init__(self, state):
        self.state = state

        self._main_windows = []           # головні вікна в порядку відкриття
        self._note_windows = {}           # note_id -> NoteWindow
        self._next_number = 1

        self.state.note_removed.connect(self.close_note)
        # одна помилка - одне повідомлення, хоч би скільки вікон було відкрито
        self.state.error_occurred.connect(self.show_error)

    # --- відкриття ----------------------------------------------------------

    def open_main_window(self):
        number = self._next_number
        self._next_number += 1

        window = MainWindow(self.state, self, number)
        window.closed.connect(lambda: self.forget_main_window(window))

        if self._main_windows:
            # кожне наступне вікно зсувається від останнього, щоб не лягти поверх
            last = self._main_windows[-1]
            window.resize(last.size())
            window.move(last.x() + config.CASCADE_STEP, last.y() + config.CASCADE_STEP)
        else:
            window.resize(900, 560)

        self._main_windows.append(window)
        window.show()
        return window

    def open_note(self, note_id):
        if self.state.find(note_id) is None:
            return None

        window = self._note_windows.get(note_id)
        if window is None:
            window = NoteWindow(self.state, note_id)
            window.closed.connect(self.forget_note_window)
            window.resize(460, 360)
            self._note_windows[note_id] = window

        # повторне відкриття не створює копію, а піднімає наявне вікно
        window.show()
        window.raise_()
        window.activateWindow()
        return window

    def open_preferences(self, parent):
        # модальний діалог: exec() повертає результат, коли діалог закрито
        return PreferencesDialog(self.state, parent).exec()

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

        # закрилось останнє головне вікно - допоміжним нема біля чого жити
        if not self._main_windows:
            self.close_all_notes()

    # --- помилки ------------------------------------------------------------

    def show_error(self, message):
        parent = QApplication.activeWindow()
        if parent is None and self._main_windows:
            parent = self._main_windows[-1]
        QMessageBox.warning(parent, config.APP_TITLE, message)
