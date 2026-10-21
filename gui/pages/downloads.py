from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QPushButton,
    QStackedWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from ..models import DownloadQueueModel, QueueStats, StatusDelegate
from ..widgets import Card, EmptyState


class DownloadsPage(QWidget):
    clear_requested = Signal()
    open_requested = Signal()
    reveal_requested = Signal(Path)

    def __init__(self, model: DownloadQueueModel) -> None:
        super().__init__()
        self._model = model
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title_column = QVBoxLayout()
        title_column.setSpacing(3)
        title = QLabel("Cola de descargas")
        title.setObjectName("SectionTitle")
        title_column.addWidget(title)
        self.summary = QLabel("Sin actividad")
        self.summary.setObjectName("Muted")
        title_column.addWidget(self.summary)
        header.addLayout(title_column, 1)

        self.open_button = QPushButton("Abrir carpeta")
        self.open_button.setObjectName("Ghost")
        self.open_button.clicked.connect(self.open_requested)
        header.addWidget(self.open_button)

        self.clear_button = QPushButton("Limpiar terminadas")
        self.clear_button.setObjectName("Ghost")
        self.clear_button.clicked.connect(self.clear_requested)
        header.addWidget(self.clear_button)
        layout.addLayout(header)

        self.table = QTableView()
        self.table.setModel(model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(58)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for column, width in ((1, 142), (2, 84), (3, 96), (4, 220)):
            self.table.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.Fixed,
            )
            self.table.setColumnWidth(column, width)
        self.table.setTextElideMode(Qt.ElideMiddle)
        self.table.setItemDelegateForColumn(1, StatusDelegate(self.table))
        self.table.doubleClicked.connect(self._on_double_click)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.table)
        self.empty = EmptyState(
            "La cola está vacía",
            "Arrastra un enlace o usa el buscador principal para descargar.",
        )
        self.stack.addWidget(self.empty)
        self.stack.setCurrentWidget(self.empty)
        table_card = Card()
        table_card.content.addWidget(self.stack, 1)
        layout.addWidget(table_card, 1)

        model.rowsInserted.connect(self._sync_empty)
        model.rowsRemoved.connect(self._sync_empty)
        model.modelReset.connect(self._sync_empty)

    def set_stats(self, stats: QueueStats) -> None:
        parts = [f"{stats.running} activas", f"{stats.queued} en espera"]
        if stats.finished:
            parts.append(f"{stats.finished} terminadas")
        if stats.failed:
            parts.append(f"{stats.failed} con error")
        self.summary.setText(" · ".join(parts) if stats.total else "Sin actividad")

    def _sync_empty(self) -> None:
        self.stack.setCurrentWidget(
            self.empty if self._model.rowCount() == 0 else self.table
        )

    def _on_double_click(self, index) -> None:
        if not index.isValid():
            return
        item = self._model.items[index.row()]
        if item.output_path:
            self.reveal_requested.emit(item.output_path)

    def _show_context_menu(self, position) -> None:
        index = self.table.indexAt(position)
        if not index.isValid():
            return
        item = self._model.items[index.row()]
        menu = QMenu(self)
        open_action = QAction("Abrir archivo", menu)
        open_action.setEnabled(item.output_path is not None)
        open_action.triggered.connect(
            lambda: self.reveal_requested.emit(item.output_path)
            if item.output_path
            else None
        )
        copy_action = QAction("Copiar URL", menu)
        copy_action.triggered.connect(
            lambda: QGuiApplication.clipboard().setText(item.url)
        )
        menu.addAction(open_action)
        menu.addAction(copy_action)
        menu.exec(self.table.viewport().mapToGlobal(position))
