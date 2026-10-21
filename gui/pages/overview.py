from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
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
from ..widgets import (
    Card,
    EmptyState,
    FeatureCard,
    HeroCard,
    LogConsole,
    StatCard,
    StatusPill,
)


class PageScroll(QScrollArea):
    def __init__(self) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.setObjectName("PageScroll")
        self.viewport().setObjectName("PageViewport")
        self._content = QWidget()
        self._content.setObjectName("PageContent")
        self._content.setMaximumWidth(1180)
        self._content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(22)
        wrapper = QWidget()
        wrapper.setObjectName("PageWrapper")
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 8, 0)
        wrapper_layout.setSpacing(0)
        wrapper_layout.addWidget(self._content, 0, Qt.AlignHCenter)
        self.setWidget(wrapper)
        for widget in (self, self.viewport(), wrapper, self._content):
            widget.setAutoFillBackground(False)
        self.setStyleSheet(
            "QScrollArea#PageScroll { background: #f4f1ea; } "
            "QWidget#PageViewport { background: #f4f1ea; } "
            "QWidget#PageWrapper { background: #f4f1ea; } "
            "QWidget#PageContent { background: transparent; }"
        )

    @property
    def content(self) -> QVBoxLayout:
        return self._layout

    def resizeEvent(self, event) -> None:
        available = max(320, self.viewport().width() - 16)
        self._content.setFixedWidth(min(1180, available))
        super().resizeEvent(event)


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

        color = QColor(STATUS_COLORS[item.status])
        pill = StatusPill(STATUS_LABELS[item.status], self._tone(item.status))
        pill.setStyleSheet(
            "QLabel#Pill { background: "
            f"rgba({color.red()}, {color.green()}, {color.blue()}, 0.12); "
            f"color: {color.name()}; border: none; }}"
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
        self.hero = HeroCard(QColor(accent.primary), QColor(accent.secondary))
        self.hero.download_requested.connect(self.download_requested)
        self.content.addWidget(self.hero)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        self.session_stat = StatCard("Sesión", "—", "#2563eb")
        self.tool_stat = StatCard("yt-dlp", "—", "#6d5ef7")
        self.queue_stat = StatCard("En cola", "0", "#d97706")
        self.completed_stat = StatCard("Completadas", "0", "#059669")
        for card in (
            self.session_stat,
            self.tool_stat,
            self.queue_stat,
            self.completed_stat,
        ):
            stats_row.addWidget(card, 1)
        self.content.addLayout(stats_row)

        features_header = QVBoxLayout()
        features_header.setSpacing(4)
        features_title = QLabel("Hecho para descargar, no para esperar.")
        features_title.setObjectName("Title")
        features_text = QLabel(
            "El mismo motor confiable de gdrive-dl, ahora con una interfaz "
            "que se siente como una web."
        )
        features_text.setObjectName("Subtitle")
        features_text.setWordWrap(True)
        features_header.addWidget(features_title)
        features_header.addWidget(features_text)
        self.content.addLayout(features_header)

        features = QHBoxLayout()
        features.setSpacing(16)
        features.addWidget(
            FeatureCard(
                "01",
                "Sesión aislada",
                "Chrome se abre con un perfil dedicado. Tu navegador de todos "
                "los días no se toca.",
                "#6d5ef7",
            ),
            1,
        )
        features.addWidget(
            FeatureCard(
                "02",
                "Descargas resilientes",
                "Timeouts, reintentos y un proceso separado para que la "
                "interfaz nunca se congele.",
                "#2563eb",
            ),
            1,
        )
        features.addWidget(
            FeatureCard(
                "03",
                "Todo local",
                "Sin servidores intermedios. La aplicación habla directo con "
                "Drive a través de yt-dlp.",
                "#059669",
            ),
            1,
        )
        self.content.addLayout(features)

        activity_header = QHBoxLayout()
        activity_title = QLabel("Actividad")
        activity_title.setObjectName("Title")
        activity_header.addWidget(activity_title)
        activity_header.addStretch(1)
        self.refresh_button = QPushButton("Actualizar")
        self.refresh_button.setObjectName("Ghost")
        activity_header.addWidget(self.refresh_button)
        self.content.addLayout(activity_header)

        lower = QHBoxLayout()
        lower.setSpacing(16)

        recent_card = Card()
        recent_title = QLabel("Descargas recientes")
        recent_title.setObjectName("SectionTitle")
        recent_card.content.addWidget(recent_title)
        self.recent_container = QWidget()
        self.recent_layout = QVBoxLayout(self.recent_container)
        self.recent_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_layout.setSpacing(8)
        recent_card.content.addWidget(self.recent_container)
        self.recent_empty = EmptyState(
            "Todavía no hay descargas",
            "Pega un enlace en el buscador de arriba para empezar.",
        )
        self.recent_layout.addWidget(self.recent_empty)
        lower.addWidget(recent_card, 3)

        activity_card = QFrame()
        activity_card.setObjectName("DarkCard")
        activity_layout = QVBoxLayout(activity_card)
        activity_layout.setContentsMargins(20, 20, 20, 20)
        activity_layout.setSpacing(12)
        live_title = QLabel("Actividad en vivo")
        live_title.setStyleSheet(
            "color: #f7f4ed; font-size: 20px; font-weight: 750; "
            "letter-spacing: -0.4px;"
        )
        activity_layout.addWidget(live_title)
        self.console = LogConsole()
        activity_layout.addWidget(self.console, 1)

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
        activity_layout.addLayout(actions)
        lower.addWidget(activity_card, 2)
        self.content.addLayout(lower)

        footer = QLabel("gdrive-dl-gui · Qt nativo · sin HTML")
        footer.setObjectName("Footer")
        footer.setAlignment(Qt.AlignCenter)
        self.content.addWidget(footer)
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
        self.tool_stat.set_value(
            status.yt_dlp_version or "No disponible",
            "Motor de descarga",
        )
        self.login_button.setText(
            "Renovar sesión" if session.available else "Iniciar sesión"
        )

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
                "Pega un enlace en el buscador de arriba para empezar.",
            )
            self.recent_layout.addWidget(self.recent_empty)
            return
        for item in list(reversed(items))[:5]:
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
