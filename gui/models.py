from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem

from gdrive_dl.errors import GdriveError
from gdrive_dl.models import DownloadResult
from gdrive_dl.models import DownloadStatus as CoreDownloadStatus

_EMPTY_INDEX = QModelIndex()


class DownloadStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


STATUS_LABELS = {
    DownloadStatus.QUEUED: "En cola",
    DownloadStatus.RUNNING: "Descargando",
    DownloadStatus.COMPLETED: "Completado",
    DownloadStatus.SKIPPED: "Omitido",
    DownloadStatus.FAILED: "Error",
}

STATUS_COLORS = {
    DownloadStatus.QUEUED: "#8ba0bd",
    DownloadStatus.RUNNING: "#67e8f9",
    DownloadStatus.COMPLETED: "#6ee7b7",
    DownloadStatus.SKIPPED: "#fcd34d",
    DownloadStatus.FAILED: "#fda4af",
}


@dataclass(slots=True)
class DownloadItem:
    identifier: int
    url: str
    status: DownloadStatus = DownloadStatus.QUEUED
    message: str = ""
    attempts: int = 0
    duration_seconds: float = 0.0
    output_path: Path | None = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True, slots=True)
class QueueStats:
    queued: int
    running: int
    completed: int
    skipped: int
    failed: int

    @property
    def finished(self) -> int:
        return self.completed + self.skipped

    @property
    def total(self) -> int:
        return self.queued + self.running + self.finished + self.failed


class DownloadQueueModel(QAbstractTableModel):
    HEADERS = ("ARCHIVO / URL", "ESTADO", "INTENTOS", "DURACIÓN", "RESULTADO")

    def __init__(self) -> None:
        super().__init__()
        self._items: list[DownloadItem] = []
        self._next_identifier = 1
        self._phase = 0.0

    @property
    def items(self) -> tuple[DownloadItem, ...]:
        return tuple(self._items)

    @property
    def phase(self) -> float:
        return self._phase

    def bump_phase(self) -> None:
        self._phase = (self._phase + 0.045) % (math.pi * 2)
        if any(item.status is DownloadStatus.RUNNING for item in self._items):
            running_rows = self._running_rows()
            if running_rows:
                self.dataChanged.emit(
                    self.index(running_rows[0], 1),
                    self.index(running_rows[-1], 1),
                    [Qt.DisplayRole],
                )

    def rowCount(self, parent: QModelIndex = _EMPTY_INDEX) -> int:
        return 0 if parent.isValid() else len(self._items)

    def columnCount(self, parent: QModelIndex = _EMPTY_INDEX) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None
        item = self._items[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == 0:
                return item.url
            if column == 1:
                return STATUS_LABELS[item.status]
            if column == 2:
                return str(item.attempts) if item.attempts else "—"
            if column == 3:
                return self._format_duration(item.duration_seconds)
            if column == 4:
                return item.message
        if role == Qt.ToolTipRole:
            if column == 0:
                return item.url
            if column == 4 and item.output_path:
                return str(item.output_path)
            return item.message or None
        if role == Qt.UserRole:
            return item.status
        if role == Qt.TextAlignmentRole and column in (2, 3):
            return int(Qt.AlignCenter)
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal and 0 <= section < len(self.HEADERS):
            return self.HEADERS[section]
        return None

    def add_item(self, url: str) -> int:
        identifier = self._next_identifier
        self._next_identifier += 1
        row = len(self._items)
        self.beginInsertRows(QModelIndex(), row, row)
        self._items.append(DownloadItem(identifier=identifier, url=url))
        self.endInsertRows()
        return identifier

    def start_item(self, identifier: int) -> None:
        self._update_item(identifier, status=DownloadStatus.RUNNING)

    def finish_item(self, identifier: int, result: DownloadResult) -> None:
        status = (
            DownloadStatus.SKIPPED
            if result.status is CoreDownloadStatus.SKIPPED
            else DownloadStatus.COMPLETED
        )
        self._update_item(
            identifier,
            status=status,
            message=result.message,
            attempts=result.attempts,
            duration_seconds=result.duration_seconds,
            output_path=result.output_path,
        )

    def fail_item(self, identifier: int, exc: BaseException) -> None:
        message = str(exc)
        if isinstance(exc, GdriveError) and exc.hint:
            message = f"{message} · {exc.hint}"
        self._update_item(identifier, status=DownloadStatus.FAILED, message=message)

    def clear_finished(self) -> None:
        keep = [
            item
            for item in self._items
            if item.status not in {
                DownloadStatus.COMPLETED,
                DownloadStatus.SKIPPED,
                DownloadStatus.FAILED,
            }
        ]
        if len(keep) == len(self._items):
            return
        self.beginResetModel()
        self._items = keep
        self.endResetModel()

    def stats(self) -> QueueStats:
        counts = {status: 0 for status in DownloadStatus}
        for item in self._items:
            counts[item.status] += 1
        return QueueStats(
            queued=counts[DownloadStatus.QUEUED],
            running=counts[DownloadStatus.RUNNING],
            completed=counts[DownloadStatus.COMPLETED],
            skipped=counts[DownloadStatus.SKIPPED],
            failed=counts[DownloadStatus.FAILED],
        )

    def active_items(self) -> tuple[DownloadItem, ...]:
        return tuple(
            item
            for item in self._items
            if item.status in {DownloadStatus.QUEUED, DownloadStatus.RUNNING}
        )

    def _running_rows(self) -> list[int]:
        return [
            row
            for row, item in enumerate(self._items)
            if item.status is DownloadStatus.RUNNING
        ]

    def _update_item(self, identifier: int, **changes) -> None:
        for row, item in enumerate(self._items):
            if item.identifier != identifier:
                continue
            for key, value in changes.items():
                setattr(item, key, value)
            self.dataChanged.emit(
                self.index(row, 0),
                self.index(row, len(self.HEADERS) - 1),
            )
            return

    @staticmethod
    def _format_duration(seconds: float) -> str:
        if seconds <= 0:
            return "—"
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes, remainder = divmod(int(seconds), 60)
        return f"{minutes}m {remainder:02d}s"


class StatusDelegate(QStyledItemDelegate):
    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> None:
        status = index.data(Qt.UserRole)
        if not isinstance(status, DownloadStatus):
            super().paint(painter, option, index)
            return

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        color = QColor(STATUS_COLORS[status])
        rect = option.rect.adjusted(6, 8, -6, -8)
        pill_width = min(rect.width(), 118)
        pill = QRectF(rect.x(), rect.y(), pill_width, rect.height())
        background = QColor(color)
        background.setAlpha(24)
        path = QPainterPath()
        path.addRoundedRect(pill, 9, 9)
        painter.fillPath(path, background)

        dot_x = pill.x() + 12
        dot_y = pill.center().y()
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(dot_x - 3, dot_y - 3, 6, 6))

        font = QFont(option.font)
        font.setPointSizeF(max(8.0, option.font.pointSizeF() - 1.0))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(color)
        text_rect = pill.adjusted(24, 0, -8, 0)
        painter.drawText(
            text_rect,
            int(Qt.AlignVCenter | Qt.AlignLeft),
            STATUS_LABELS[status],
        )

        if status is DownloadStatus.RUNNING:
            phase = getattr(index.model(), "phase", 0.0)
            progress = (math.sin(phase) + 1.0) / 2.0
            bar = QRectF(
                pill.x() + 10,
                pill.bottom() - 4,
                max(8.0, (pill.width() - 20) * progress),
                2,
            )
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(bar, 1, 1)
        painter.restore()
