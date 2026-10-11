"""Константи застосунку. Оголошуються тут і тільки тут."""

STUDENT_NAME = "Andrii Zelyuk"                # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"                       # група
DB_FILE = "workspace_andrii_zelyuk.db"        # файл бази з практичних 3-5
APP_TITLE = "Notes Manager"                   # назва застосунку

# --- П8: багатовіконність ---
CASCADE_STEP = 40                             # зсув кожного наступного вікна, пікселів
DEFAULT_PREVIEW_LENGTH = 30                   # символів тексту нотатки в коротких підписах

# --- П9: таблиця ---
TABLE_PREVIEW_LENGTH = 40                     # символів тіла нотатки в колонці Preview
LONG_NOTE_CHARS = 200                         # від якої довжини нотатка вважається довгою
EMPTY_TABLE_TEXT = "No notes to show"         # текст, коли таблиця порожня

# --- П11: налаштування, лог, обробка помилок ---
ORG_NAME = "KTBP"                             # для QSettings і QStandardPaths
LOG_FILE = "notes_manager.log"                # ім'я файла лога
LOG_MAX_BYTES = 1_000_000                     # розмір, після якого файл ротується
LOG_BACKUP_COUNT = 3                          # скільки старих файлів лога тримати
RECENT_EXPORTS_MAX = 5                        # довжина списку останніх експортів

LOGO_FILE = "assets/logo.png"                   # іконка вікон (ресурс з практичної про PyInstaller)

AUTHOR = f"{STUDENT_NAME}, {STUDENT_GROUP}"
MAIN_WINDOW_TITLE = f"{APP_TITLE} - {AUTHOR}"
