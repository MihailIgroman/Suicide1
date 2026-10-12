# Точка збірки: тут і тільки тут шари зустрічаються.
#
# Запуск із кореня проєкту:  python main.py

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app import config
from app.state import AppState
from app.storage import SqliteStorage
from app.ui.main_window import MainWindow

# база лежить поруч із main.py, звідки б не запускали застосунок
BASE_DIR = Path(__file__).resolve().parent

# три стартові нотатки для першого запуску, коли бази ще немає
SEED_NOTES = [
    "Read the lecture about app state",
    "Split notes_manager.py into layers",
    "Check that two windows show the same data",
]


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_TITLE)

    db_path = BASE_DIR / config.DB_FILE
    first_run = not db_path.exists()

    storage = SqliteStorage(db_path)          # 1. сховище
    state = AppState(storage)                 # 2. стан отримує сховище

    window = MainWindow(state)                # 3. вікно отримує стан
    window.resize(900, 560)
    window.show()

    # 4. дані - після вікна: якщо база не читається, помилку вже є кому показати
    state.load()

    if first_run:
        for text in SEED_NOTES:
            state.add_note(text)
        state.save()
        state.select(-1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
