from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gdrive_dl.models import SystemStatus

from ..widgets import Card, StatusPill
from .overview import PageScroll


class SessionPage(PageScroll):
    login_requested = Signal()
    refresh_requested = Signal()
    open_profile_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.content.setContentsMargins(0, 0, 0, 0)

        hero = Card()
        top = QHBoxLayout()
        title_column = QVBoxLayout()
        title_column.setSpacing(4)
        title = QLabel("Sesión de Google")
        title.setObjectName("SectionTitle")
        subtitle = QLabel(
            "gdrive-dl usa un perfil de Chrome aislado. Tu navegador diario "
            "no se modifica."
        )
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)
        title_column.addWidget(title)
        title_column.addWidget(subtitle)
        top.addLayout(title_column, 1)
        self.pill = StatusPill("Verificando…", "muted")
        top.addWidget(self.pill)
        hero.content.addLayout(top)

        details = QWidget()
        grid = QGridLayout(details)
        grid.setContentsMargins(0, 8, 0, 8)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(14)
        self.cookie_value = self._detail(grid, 0, "Cookies de autenticación")
        self.profile_value = self._detail(grid, 1, "Perfil de Chrome")
        self.cookie_db_value = self._detail(grid, 2, "Base de cookies")
        hero.content.addWidget(details)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        self.login_button = QPushButton("Iniciar sesión con Chrome")
        self.login_button.setObjectName("Primary")
        self.login_button.clicked.connect(self.login_requested)
        action_row.addWidget(self.login_button)
        self.refresh_button = QPushButton("Actualizar estado")
        self.refresh_button.setObjectName("Ghost")
        self.refresh_button.clicked.connect(self.refresh_requested)
        action_row.addWidget(self.refresh_button)
        self.open_button = QPushButton("Abrir perfil")
        self.open_button.setObjectName("Ghost")
        self.open_button.clicked.connect(self.open_profile_requested)
        action_row.addWidget(self.open_button)
        action_row.addStretch(1)
        hero.content.addLayout(action_row)
        self.content.addWidget(hero)

        steps = Card()
        steps_title = QLabel("Cómo funciona")
        steps_title.setObjectName("SectionTitle")
        steps.content.addWidget(steps_title)
        for number, title_text, body in (
            (
                "01",
                "Abre Chrome",
                "Se lanza una ventana con un --user-data-dir dedicado.",
            ),
            (
                "02",
                "Inicia sesión",
                "Completa el login de Google y cierra todas las ventanas de Chrome.",
            ),
            (
                "03",
                "Verifica",
                "La app lee nombres de cookies en modo solo lectura y confirma la sesión.",
            ),
            (
                "04",
                "Descarga",
                "yt-dlp usa el perfil aislado con --cookies-from-browser.",
            ),
        ):
            row = QHBoxLayout()
            row.setSpacing(12)
            badge = QLabel(number)
            badge.setFixedWidth(34)
            badge.setStyleSheet(
                "color: #8b5cf6; font-weight: 800; font-size: 12px;"
            )
            row.addWidget(badge)
            text_column = QVBoxLayout()
            text_column.setSpacing(2)
            step_title = QLabel(title_text)
            step_title.setStyleSheet("font-weight: 700; color: #e6edf7;")
            step_body = QLabel(body)
            step_body.setWordWrap(True)
            step_body.setObjectName("Muted")
            text_column.addWidget(step_title)
            text_column.addWidget(step_body)
            row.addLayout(text_column, 1)
            steps.content.addLayout(row)
        self.content.addWidget(steps)
        self.content.addStretch(1)

    @staticmethod
    def _detail(grid: QGridLayout, row: int, caption: str) -> QLabel:
        caption_label = QLabel(caption)
        caption_label.setObjectName("Muted")
        value = QLabel("—")
        value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        value.setWordWrap(True)
        grid.addWidget(caption_label, row, 0)
        grid.addWidget(value, row, 1)
        grid.setColumnStretch(1, 1)
        return value

    def set_status(self, status: SystemStatus) -> None:
        session = status.session
        if session.available:
            self.pill.set_state("Sesión válida", "success")
            self.login_button.setText("Renovar sesión")
        elif session.cookie_db is None:
            self.pill.set_state("Sin perfil", "warning")
            self.login_button.setText("Iniciar sesión con Chrome")
        else:
            self.pill.set_state("Sesión incompleta", "danger")
            self.login_button.setText("Volver a iniciar sesión")
        self.cookie_value.setText(
            f"{session.google_auth_cookie_count} cookies de Google"
            if session.google_auth_cookie_count
            else (session.reason or "No se encontraron cookies")
        )
        self.profile_value.setText(str(session.profile_dir))
        self.cookie_db_value.setText(
            str(session.cookie_db) if session.cookie_db else "No disponible"
        )

    def set_busy(self, busy: bool) -> None:
        self.login_button.setDisabled(busy)
        self.refresh_button.setDisabled(busy)
        if busy:
            self.login_button.setText("Esperando a Chrome…")
