"""Панель зі списком нотаток: QTableView над NoteTableModel."""

from PySide6.QtCore import QSortFilterProxyModel, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QStackedLayout,
    QTableView,
    QWidget,
)

from .. import config
from ..state import NO_SELECTION
from .note_table_model import NoteTableModel


class NoteListPanel(QWidget):
    """Таблиця нотаток. Виділення синхронізує зі станом за id, а не за рядком."""

    open_requested = Signal(int)      # подвійне клацання: відкрити нотатку у вікні

    def __init__(self, state, preview_length, parent=None):
        super().__init__(parent)

        self.state = state
        self._syncing = False         # захист від петлі стан <-> виділення

        self.model = NoteTableModel(state, preview_length, self)
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setSortRole(Qt.ItemDataRole.EditRole)

        self._build_ui()
        self._connect()

        self._update_empty()
        self.render_selection()

    def _build_ui(self):
        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        # -1: без сортування, тобто порядок стану (закріплені першими);
        # клацання по заголовку колонки вмикає сортування за нею
        self.table.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        self.table.setSortingEnabled(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(NoteTableModel.COL_PREVIEW, QHeaderView.ResizeMode.Stretch)

        self.empty_label = QLabel(config.EMPTY_TABLE_TEXT)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: gray;")

        self._stack = QStackedLayout(self)
        self._stack.addWidget(self.table)
        self._stack.addWidget(self.empty_label)

    def _connect(self):
        self.table.selectionModel().currentChanged.connect(self._on_current_changed)
        self.table.doubleClicked.connect(self._on_double_clicked)

        for signal in (self.proxy.modelReset, self.proxy.rowsInserted, self.proxy.rowsRemoved):
            signal.connect(self._update_empty)

        # модель під'єдналась до notes_changed раніше (у своєму конструкторі),
        # тому тут вона вже перебудована
        self.state.notes_changed.connect(self.render_selection)
        self.state.selection_changed.connect(self.render_selection)

    # --- наміри користувача ---

    def current_note_id(self):
        index = self.table.currentIndex()
        if not index.isValid():
            return None
        return self.model.note_id_at(self.proxy.mapToSource(index).row())

    def _on_current_changed(self, current, previous):
        if self._syncing:
            return

        note_id = self.current_note_id()
        self.state.select(note_id if note_id is not None else NO_SELECTION)

    def _on_double_clicked(self, index):
        note_id = self.model.note_id_at(self.proxy.mapToSource(index).row())
        if note_id is not None:
            self.open_requested.emit(note_id)

    # --- перемальовування ---

    def set_preview_length(self, length):
        self.model.set_preview_length(length)

    def render_selection(self, note_id=None):
        selected_id = self.state.selected_id()

        self._syncing = True
        try:
            if selected_id == NO_SELECTION:
                self.table.clearSelection()
                self.table.setCurrentIndex(self.proxy.index(-1, -1))
                return

            row = self.model.row_of(selected_id)
            if row < 0:
                return

            proxy_index = self.proxy.mapFromSource(self.model.index(row, NoteTableModel.COL_PREVIEW))
            if proxy_index.isValid():
                self.table.setCurrentIndex(proxy_index)
                self.table.scrollTo(proxy_index)
        finally:
            self._syncing = False

    def _update_empty(self):
        empty = self.proxy.rowCount() == 0
        self._stack.setCurrentWidget(self.empty_label if empty else self.table)
