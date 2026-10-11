"""Шар налаштувань. Єдине місце в проєкті, яке знає про QSettings.

Ключі, типи, типові значення й межі живуть тут. Решта коду пише
settings.font_size і нічого не знає про рядки-ключі.
Файл налаштувань - зовнішні дані: кожне значення перевіряється при читанні.
"""

import logging
from pathlib import Path

from PySide6.QtCore import QByteArray, QObject, QSettings, QStandardPaths, Signal

from . import config

logger = logging.getLogger(__name__)

# --- ключі: кожен рядок існує в проєкті рівно один раз ---
KEY_FONT_SIZE = "ui/font_size"
KEY_PREVIEW_LENGTH = "ui/preview_length"
KEY_AUTOSAVE = "editor/autosave"
KEY_AUTOSAVE_INTERVAL = "editor/autosave_interval_s"
KEY_CONFIRM_DELETE = "editor/confirm_delete"
KEY_LOG_LEVEL = "logging/level"
KEY_WINDOW_GEOMETRY = "window/geometry"
KEY_WINDOW_STATE = "window/state"
WINDOW_GROUP = "window"
RECENT_EXPORTS_ARRAY = "exports/recent"
RECENT_EXPORT_PATH = "path"

# --- типові значення й межі ---
FONT_SIZE_DEFAULT, FONT_SIZE_MIN, FONT_SIZE_MAX = 12, 8, 32
PREVIEW_DEFAULT, PREVIEW_MIN, PREVIEW_MAX = config.TABLE_PREVIEW_LENGTH, 10, 200
INTERVAL_DEFAULT, INTERVAL_MIN, INTERVAL_MAX = 30, 5, 600
LOG_LEVELS = ("INFO", "DEBUG")

_TRUE_WORDS = ("true", "1", "yes", "on")
_FALSE_WORDS = ("false", "0", "no", "off")


def default_settings_path():
    """settings.ini у каталозі конфігурації користувача (від QStandardPaths)."""
    base = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppConfigLocation
    )
    return Path(base) / "settings.ini"


class AppSettings(QObject):
    """Єдина точка доступу до налаштувань."""

    changed = Signal()                  # змінились налаштування користувача
    recent_exports_changed = Signal()   # змінився список останніх експортів

    def __init__(self, path=None, parent=None):
        super().__init__(parent)

        if path is None:
            path = default_settings_path()

        # INI-файл замість реєстру Windows: його видно, і його можна
        # зіпсувати руками, щоб перевірити стійкість застосунку
        self._settings = QSettings(str(path), QSettings.Format.IniFormat)

        if self._settings.status() != QSettings.Status.NoError:
            logger.warning(
                "Settings file is unreadable (%s), defaults are used: %s",
                self._settings.status().name,
                self._settings.fileName(),
            )
        logger.info("Settings file: %s", self._settings.fileName())

    def file_name(self):
        return self._settings.fileName()

    # --- безпечне читання ---------------------------------------------------
    # QSettings на сміття відповідає мовчки: "abc" з type=int стає 0,
    # "maybe" з type=bool стає True. Тому читаємо сире значення й
    # перевіряємо самі; про кожне погане значення - WARNING у лог.

    def _read_int(self, key, default, low, high):
        raw = self._settings.value(key, default)
        try:
            value = int(raw)
        except (TypeError, ValueError):
            logger.warning("Bad value %r for %s, using %s", raw, key, default)
            return default

        if not low <= value <= high:
            clamped = min(max(value, low), high)
            logger.warning("Value %s for %s is out of range, using %s", value, key, clamped)
            return clamped

        return value

    def _read_bool(self, key, default):
        raw = self._settings.value(key, default)
        if isinstance(raw, bool):
            return raw

        text = str(raw).strip().lower()
        if text in _TRUE_WORDS:
            return True
        if text in _FALSE_WORDS:
            return False

        logger.warning("Bad value %r for %s, using %s", raw, key, default)
        return default

    def _read_bytes(self, key):
        raw = self._settings.value(key, QByteArray())
        if isinstance(raw, QByteArray):
            return raw

        logger.warning("Bad value for %s, ignoring it", key)
        return QByteArray()

    def _write(self, key, value):
        self._settings.setValue(key, value)

    # --- налаштування користувача --------------------------------------------

    @property
    def font_size(self):
        return self._read_int(KEY_FONT_SIZE, FONT_SIZE_DEFAULT, FONT_SIZE_MIN, FONT_SIZE_MAX)

    @property
    def preview_length(self):
        return self._read_int(KEY_PREVIEW_LENGTH, PREVIEW_DEFAULT, PREVIEW_MIN, PREVIEW_MAX)

    @property
    def autosave(self):
        return self._read_bool(KEY_AUTOSAVE, True)

    @property
    def autosave_interval_s(self):
        return self._read_int(
            KEY_AUTOSAVE_INTERVAL, INTERVAL_DEFAULT, INTERVAL_MIN, INTERVAL_MAX
        )

    @property
    def confirm_delete(self):
        return self._read_bool(KEY_CONFIRM_DELETE, True)

    @property
    def log_level(self):
        raw = str(self._settings.value(KEY_LOG_LEVEL, "INFO")).strip().upper()
        if raw in LOG_LEVELS:
            return raw

        logger.warning("Bad value %r for %s, using INFO", raw, KEY_LOG_LEVEL)
        return "INFO"

    def values(self):
        """Усі налаштування користувача одним словником (для діалогу)."""
        return {
            "font_size": self.font_size,
            "preview_length": self.preview_length,
            "autosave": self.autosave,
            "autosave_interval_s": self.autosave_interval_s,
            "confirm_delete": self.confirm_delete,
            "log_level": self.log_level,
        }

    def apply(self, values):
        """Записує налаштування з діалогу. Сигнал changed - один раз на все."""
        level = str(values["log_level"]).upper()
        if level not in LOG_LEVELS:
            raise ValueError(f"Unknown log level: {level}")

        self._write(KEY_FONT_SIZE, min(max(int(values["font_size"]), FONT_SIZE_MIN), FONT_SIZE_MAX))
        self._write(KEY_PREVIEW_LENGTH, min(max(int(values["preview_length"]), PREVIEW_MIN), PREVIEW_MAX))
        self._write(KEY_AUTOSAVE, bool(values["autosave"]))
        self._write(
            KEY_AUTOSAVE_INTERVAL,
            min(max(int(values["autosave_interval_s"]), INTERVAL_MIN), INTERVAL_MAX),
        )
        self._write(KEY_CONFIRM_DELETE, bool(values["confirm_delete"]))
        self._write(KEY_LOG_LEVEL, level)
        self.sync()

        logger.info("Settings saved: %s", values)
        self.changed.emit()

    # --- останні експорти (масив QSettings) ---------------------------------

    def recent_exports(self):
        paths = []
        count = self._settings.beginReadArray(RECENT_EXPORTS_ARRAY)
        try:
            for index in range(count):
                self._settings.setArrayIndex(index)
                value = self._settings.value(RECENT_EXPORT_PATH, "")
                if isinstance(value, str) and value:
                    paths.append(value)
        finally:
            self._settings.endArray()

        return paths[: config.RECENT_EXPORTS_MAX]

    def add_recent_export(self, path):
        path = str(path)
        paths = [p for p in self.recent_exports() if p != path]
        paths.insert(0, path)
        self._write_recent(paths[: config.RECENT_EXPORTS_MAX])

    def clear_recent_exports(self):
        self._write_recent([])

    def _write_recent(self, paths):
        self._settings.remove(RECENT_EXPORTS_ARRAY)
        self._settings.beginWriteArray(RECENT_EXPORTS_ARRAY, len(paths))
        try:
            for index, path in enumerate(paths):
                self._settings.setArrayIndex(index)
                self._settings.setValue(RECENT_EXPORT_PATH, path)
        finally:
            self._settings.endArray()

        self.sync()
        self.recent_exports_changed.emit()

    # --- стан інтерфейсу ----------------------------------------------------

    def window_geometry(self):
        return self._read_bytes(KEY_WINDOW_GEOMETRY)

    def window_state(self):
        return self._read_bytes(KEY_WINDOW_STATE)

    def save_window(self, geometry, state):
        self._write(KEY_WINDOW_GEOMETRY, geometry)
        self._write(KEY_WINDOW_STATE, state)
        self.sync()

    def reset_window(self):
        self._settings.remove(WINDOW_GROUP)
        self.sync()

    def sync(self):
        self._settings.sync()
        if self._settings.status() == QSettings.Status.AccessError:
            # налаштування - не дані: не вийшло записати - не катастрофа
            logger.warning("Cannot write settings file: %s", self._settings.fileName())
