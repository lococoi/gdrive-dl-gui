from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gdrive_dl.models import DoctorCheck, DoctorReport

from ..widgets import Card, EmptyState, StatusPill
from .overview import PageScroll


class CheckRow(QFrame):
    def __init__(self, check: DoctorCheck) -> None:
        super().__init__()
        self.setObjectName("SubtleCard")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)
        tone = "success" if check.healthy else ("danger" if check.critical else "warning")
        pill = StatusPill("OK" if check.healthy else "Revisar", tone)
        layout.addWidget(pill)
        text = QVBoxLayout()
        text.setSpacing(2)
        name = QLabel(check.name)
        name.setStyleSheet("font-weight: 700; color: #111114;")
        detail = QLabel(check.detail)
        detail.setObjectName("Muted")
        detail.setWordWrap(True)
        text.addWidget(name)
        text.addWidget(detail)
        layout.addLayout(text, 1)


class DiagnosticsPage(PageScroll):
    run_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.content.setContentsMargins(0, 0, 0, 0)

        header = Card()
        row = QHBoxLayout()
        title_column = QVBoxLayout()
        title_column.setSpacing(3)
        title = QLabel("Diagnóstico del entorno")
        title.setObjectName("SectionTitle")
        subtitle = QLabel(
            "Comprueba Python, Chrome, yt-dlp, la sesión, permisos de escritura, "
            "dependencias y espacio libre."
        )
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)
        title_column.addWidget(title)
        title_column.addWidget(subtitle)
        row.addLayout(title_column, 1)
        self.run_button = QPushButton("Ejecutar diagnóstico")
        self.run_button.setObjectName("Primary")
        self.run_button.clicked.connect(self.run_requested)
        row.addWidget(self.run_button)
        header.content.addLayout(row)
        self.status = QLabel("Sin ejecutar")
        self.status.setObjectName("Muted")
        header.content.addWidget(self.status)
        self.content.addWidget(header)

        self.results = QWidget()
        self.results.setAutoFillBackground(False)
        self.results_layout = QVBoxLayout(self.results)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(8)
        self.empty = EmptyState(
            "Sin diagnóstico todavía",
            "Ejecuta las comprobaciones para ver el estado del entorno.",
        )
        self.results_layout.addWidget(self.empty)
        self.content.addWidget(self.results)
        self.content.addStretch(1)

    def set_busy(self, busy: bool) -> None:
        self.run_button.setDisabled(busy)
        self.run_button.setText("Ejecutando…" if busy else "Ejecutar diagnóstico")
        if busy:
            self.status.setText("Comprobando entorno…")

    def set_report(self, report: DoctorReport) -> None:
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()
        for check in report.checks:
            self.results_layout.addWidget(CheckRow(check))
        failed = len(report.failed)
        self.status.setText(
            "Todo correcto." if not failed else f"{failed} comprobación(es) con problemas."
        )
