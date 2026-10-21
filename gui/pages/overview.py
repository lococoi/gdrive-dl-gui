from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gdrive_dl.models import SystemStatus

from ..models import (
    STATUS_COLORS,
    STATUS_LABELS,
    DownloadItem,
    DownloadStatus,
    QueueStats,
)
from ..theme import ACCENTS
from ..widgets import Card, EmptyState, HeroCard, LogConsole, StatCard, StatusPill


class PageScroll(QScrollArea):
    def __init__(self) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self._content = QWidget()
        for widget in (self, self.viewport(), self._content):
            palette = widget.palette()
            palette.setColor(QPalette.Window, QColor(0, 0, 0, 0))
            palette.setColor(QPalette.Base, QColor(0, 0, 0, 0))
            widget.setPalette(palette)
            widget.setAutoFillBackground(False)
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(0, 0, 8, 0)
        self._layout.setSpacing(16)
        self.setWidget(self._content)

    @property
    def content(self) -> QVBoxLayout:
        return self._layout


class RecentRow(QFrame):
    def __init__(self, item: DownloadItem) -> None:
        super().__init__()
        self.setObjectName("SubtleCard")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        text_column = QVBoxLayout()
        text_column.setSpacing(2)
        url = QLabel(item.url)
        url.setObjectName("Muted")
        url.setToolTip(item.url)
        url.setTextInteractionFlags(Qt.TextSelectableByMouse)
        text_column.addWidget(url)

        detail = item.message or item.url
        detail_label = QLabel(detail)
        detail_label.setObjectName("Tiny")
        detail_label.setToolTip(detail)
        text_column.addWidget(detail_label)
        layout.addLayout(text_column, 1)

        color = STATUS_COLORS[item.status]
        pill = StatusPill(STATUS_LABELS[item.status], self._tone(item.status))
        pill.setStyleSheet(
            f"QLabel#Pill {{ background: {color}22; color: {color}; "
            f"border: 1px solid {color}66; }}"
        )
        layout.addWidget(pill)

    @staticmethod
    def _tone(status: DownloadStatus) -> str:
        return {
            DownloadStatus.COMPLETED: "success",
            DownloadStatus.SKIPPED: "warning",
            DownloadStatus.FAILED: "danger",
            DownloadStatus.RUNNING: "info",
            DownloadStatus.QUEUED: "muted",
        }[status]


class OverviewPage(PageScroll):
    download_requested = Signal(str)
    login_requested = Signal()
    doctor_requested = Signal()
    open_output_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        accent = ACCENTS["violet"]
        self.content.setContentsMargins(0, 0, 0, 0)
        self.hero = HeroCard(QColor(accent.primary), QColor(accent.secondary))
        self.hero.download_requested.connect(self.download_requested)
        self.content.addWidget(self.hero)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        self.session_stat = StatCard("Sesión", "—", "#22d3ee")
        self.tool_stat = StatCard("yt-dlp", "—", "#8b5cf6")
        self.queue_stat = StatCard("En cola", "0", "#fbbf24")
        self.completed_stat = StatCard("Completadas", "0", "#34d399")
        for card in (
            self.session_stat,
            self.tool_stat,
            self.queue_stat,
            self.completed_stat,
        ):
            stats_row.addWidget(card, 1)
        self.content.addLayout(stats_row)

        lower = QHBoxLayout()
        lower.setSpacing(16)

        recent_card = Card()
        recent_header = QHBoxLayout()
        recent_title = QLabel("Actividad reciente")
        recent_title.setObjectName("SectionTitle")
        recent_header.addWidget(recent_title)
        recent_header.addStretch(1)
        self.refresh_button = QPushButton("Actualizar")
        self.refresh_button.setObjectName("Ghost")
        recent_header.addWidget(self.refresh_button)
        recent_card.content.addLayout(recent_header)

        self.recent_container = QWidget()
        self.recent_layout = QVBoxLayout(self.recent_container)
        self.recent_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_layout.setSpacing(8)
        recent_card.content.addWidget(self.recent_container)
        self.recent_empty = EmptyState(
            "Todavía no hay descargas",
            "Pega un enlace arriba para iniciar la primera.",
        )
        self.recent_layout.addWidget(self.recent_empty)
        lower.addWidget(recent_card, 3)

        activity_card = Card()
        activity_header = QHBoxLayout()
        activity_title = QLabel("Actividad en vivo")
        activity_title.setObjectName("SectionTitle")
        activity_header.addWidget(activity_title)
        activity_header.addStretch(1)
        self.console = LogConsole()
        activity_card.content.addLayout(activity_header)
        activity_card.content.addWidget(self.console)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        self.login_button = QPushButton("Iniciar sesión")
        self.login_button.setObjectName("Primary")
        self.login_button.clicked.connect(self.login_requested)
        actions.addWidget(self.login_button)
        self.doctor_button = QPushButton("Diagnóstico")
        self.doctor_button.setObjectName("Ghost")
        self.doctor_button.clicked.connect(self.doctor_requested)
        actions.addWidget(self.doctor_button)
        self.open_button = QPushButton("Abrir descargas")
        self.open_button.setObjectName("Ghost")
        self.open_button.clicked.connect(self.open_output_requested)
        actions.addWidget(self.open_button)
        activity_card.content.addLayout(actions)
        lower.addWidget(activity_card, 2)

        self.content.addLayout(lower)
        self.content.addStretch(1)

    def set_accent(self, name: str) -> None:
        accent = ACCENTS.get(name, ACCENTS["violet"])
        self.hero.set_accent(QColor(accent.primary), QColor(accent.secondary))

    def set_status(self, status: SystemStatus) -> None:
        session = status.session
        if session.available:
            self.session_stat.set_value(
                "Lista",
                f"{session.google_auth_cookie_count} cookies de Google",
            )
        else:
            self.session_stat.set_value("Sin sesión", session.reason or "Ejecuta login")
        tool = status.yt_dlp_version or "No disponible"
        self.tool_stat.set_value(tool, "Motor de descarga")
        self.login_button.setText("Renovar sesión" if session.available else "Iniciar sesión")

    def set_queue_stats(self, stats: QueueStats) -> None:
        self.queue_stat.set_value(
            str(stats.queued + stats.running),
            f"{stats.running} activas · {stats.queued} esperando",
        )
        self.completed_stat.set_value(
            str(stats.finished),
            f"{stats.failed} con error" if stats.failed else "Sin errores",
        )

    def set_recent(self, items: tuple[DownloadItem, ...]) -> None:
        while self.recent_layout.count():
            child = self.recent_layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()
        if not items:
            self.recent_empty = EmptyState(
                "Todavía no hay descargas",
                "Pega un enlace arriba para iniciar la primera.",
            )
            self.recent_layout.addWidget(self.recent_empty)
            return
        for item in list(reversed(items))[:6]:
            self.recent_layout.addWidget(RecentRow(item))
        self.recent_layout.addStretch(1)

    def append_log(self, line: str) -> None:
        self.console.append_line(line)

    def set_login_busy(self, busy: bool) -> None:
        self.login_button.setDisabled(busy)
        self.login_button.setText("Esperando a Chrome…" if busy else "Iniciar sesión")

    def set_hero_busy(self, busy: bool) -> None:
        self.hero.set_busy(busy)

    def take_url(self) -> str:
        return self.hero.url_input.text().strip()

    def clear_url(self) -> None:
        self.hero.clear_url()
