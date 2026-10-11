"""Лог у файл із ротацією, повідомлення Qt у тому ж лозі, глобальний перехоплювач."""

import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PySide6.QtCore import QStandardPaths, QtMsgType, qInstallMessageHandler
from PySide6.QtWidgets import QApplication, QMessageBox

from . import config

_QT_LEVELS = {
    QtMsgType.QtDebugMsg: logging.DEBUG,
    QtMsgType.QtInfoMsg: logging.INFO,
    QtMsgType.QtWarningMsg: logging.WARNING,
    QtMsgType.QtCriticalMsg: logging.ERROR,
    QtMsgType.QtFatalMsg: logging.CRITICAL,
}

logger = logging.getLogger(__name__)


def log_directory():
    """Каталог для лога. Викликати після setOrganizationName/setApplicationName."""
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    return Path(base) / "logs"


def setup_logging(level=logging.INFO):
    """Налаштовує кореневий логер. Повертає шлях до файла лога або None."""
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging.Formatter("%(levelname)-8s %(name)s: %(message)s"))

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(console_handler)

    log_path = log_directory() / config.LOG_FILE
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=config.LOG_MAX_BYTES,
            backupCount=config.LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
    except OSError as error:
        # без файла лога застосунок працює далі - пише хоча б у консоль
        logger.warning("Cannot open log file %s: %s", log_path, error)
        return None

    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")
    )
    root.addHandler(file_handler)
    return log_path


def set_log_level(level_name):
    """Змінює рівень кореневого логера одразу, без перезапуску."""
    level = logging.DEBUG if level_name == "DEBUG" else logging.INFO
    logging.getLogger().setLevel(level)
    logger.info("Log level set to %s", level_name)


def install_qt_message_handler():
    """Перенаправляє повідомлення самого Qt у logging."""
    qt_logger = logging.getLogger("qt")

    def handler(mode, context, message):
        qt_logger.log(_QT_LEVELS.get(mode, logging.INFO), "%s", message)

    qInstallMessageHandler(handler)


def install_excepthook(log_path):
    """Ловить усе, що ніхто не спіймав: пише в лог і показує вікно."""
    state = {"busy": False}

    def hook(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return

        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_tb))

        # захист від петлі "помилка -> діалог -> помилка -> діалог"
        if state["busy"] or QApplication.instance() is None:
            return

        state["busy"] = True
        try:
            details = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            where = str(log_path) if log_path is not None else "the console (log file is unavailable)"

            box = QMessageBox(QApplication.activeWindow())
            box.setIcon(QMessageBox.Icon.Critical)
            box.setWindowTitle(config.APP_TITLE)
            box.setText("The application ran into an unexpected problem.")
            box.setInformativeText(
                f"{exc_type.__name__}: {exc_value}\n\n"
                f"Your notes are still open. Details are saved to:\n{where}"
            )
            box.setDetailedText(details)
            box.setStandardButtons(QMessageBox.StandardButton.Close)
            box.exec()
        finally:
            state["busy"] = False

    sys.excepthook = hook
