"""Точка збірки: тут і тільки тут шари зустрічаються.

Запуск із кореня проєкту:  python main.py
"""

import logging
import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QStandardPaths
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app import config
from app.logging_setup import (
    install_excepthook,
    install_qt_message_handler,
    set_log_level,
    setup_logging,
)
from app.settings import AppSettings
from app.state import AppState
from app.storage import SqliteStorage
from app.ui.window_manager import WindowManager

# каталог із файлами застосунку (ресурси лише читаємо звідси)
BASE_DIR = Path(__file__).resolve().parent


def data_directory():
    """Де лежить база.

    Звичайний запуск - поруч із main.py, як у практичних 3-9.
    Зібраний PyInstaller-ом застосунок у свій каталог писати не може,
    тому там база йде в каталог даних користувача.
    """
    if getattr(sys, "frozen", False):
        return Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
    return BASE_DIR


def main():
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName(config.ORG_NAME)
    QCoreApplication.setApplicationName(config.APP_TITLE)

    # 1. лог і перехоплювачі - якомога раніше, щоб бачити всі помилки запуску
    log_path = setup_logging(logging.INFO)
    install_qt_message_handler()
    install_excepthook(log_path)

    logger = logging.getLogger(__name__)
    logger.info("Application started (%s), log file: %s", config.AUTHOR, log_path)

    # 2. налаштування; рівень лога застосовується одразу й при кожній зміні
    settings = AppSettings()
    set_log_level(settings.log_level)
    settings.changed.connect(lambda: set_log_level(settings.log_level))

    logo_path = BASE_DIR / config.LOGO_FILE
    if logo_path.exists():
        app.setWindowIcon(QIcon(str(logo_path)))
    else:
        logger.warning("Logo not found: %s", logo_path)

    # 3. дані
    db_path = data_directory() / config.DB_FILE
    storage = SqliteStorage(db_path)
    state = AppState(storage)

    # 4. вікна; спершу вікна, потім load(): помилку читання вже є кому показати
    windows = WindowManager(state, settings, log_path)
    windows.open_main_window()

    state.load()

    exit_code = app.exec()
    settings.sync()
    logger.info("Application finished with code %s", exit_code)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
