from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..settings import GuiSettings
from ..theme import ACCENTS
from ..widgets import Card
from .overview import PageScroll


class PathField(QWidget):
    def __init__(self, value: str = "") -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self.edit = QLineEdit(value)
        layout.addWidget(self.edit, 1)
        browse = QPushButton("Examinar")
        browse.setObjectName("Ghost")
        browse.clicked.connect(self._browse)
        layout.addWidget(browse)

    def _browse(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta",
            self.edit.text() or str(Path.home()),
        )
        if selected:
            self.edit.setText(selected)

    def text(self) -> str:
        return self.edit.text().strip()

    def setText(self, value: str) -> None:
        self.edit.setText(value)


class SettingsPage(PageScroll):
    settings_saved = Signal(object)
    accent_changed = Signal(str)

    def __init__(self, settings: GuiSettings) -> None:
        super().__init__()
        self.content.setContentsMargins(0, 0, 0, 0)

        top = QHBoxLayout()
        title_column = QVBoxLayout()
        title_column.setSpacing(3)
        title = QLabel("Preferencias")
        title.setObjectName("SectionTitle")
        description = QLabel("Los cambios se aplican al guardar.")
        description.setObjectName("Muted")
        title_column.addWidget(title)
        title_column.addWidget(description)
        top.addLayout(title_column, 1)
        self.save_button = QPushButton("Guardar cambios")
        self.save_button.setObjectName("Primary")
        self.save_button.clicked.connect(self._save)
        top.addWidget(self.save_button)
        self.content.addLayout(top)

        paths = Card()
        paths_title = QLabel("Rutas")
        paths_title.setObjectName("SectionTitle")
        paths.content.addWidget(paths_title)
        form = QFormLayout()
        form.setContentsMargins(0, 2, 0, 2)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)
        self.profile_field = PathField(str(settings.profile_dir))
        self.output_field = PathField(str(settings.output_dir))
        form.addRow("Perfil de Chrome", self.profile_field)
        form.addRow("Carpeta de descargas", self.output_field)
        paths.content.addLayout(form)
        self.content.addWidget(paths)

        downloads = Card()
        downloads_title = QLabel("Descargas")
        downloads_title.setObjectName("SectionTitle")
        downloads.content.addWidget(downloads_title)
        download_form = QFormLayout()
        download_form.setContentsMargins(0, 2, 0, 2)
        download_form.setHorizontalSpacing(18)
        download_form.setVerticalSpacing(12)

        self.login_timeout = QDoubleSpinBox()
        self.login_timeout.setRange(10, 7200)
        self.login_timeout.setSuffix(" s")
        self.login_timeout.setValue(settings.login_timeout_seconds)
        download_form.addRow("Timeout de login", self.login_timeout)

        self.download_timeout = QDoubleSpinBox()
        self.download_timeout.setRange(10, 86400)
        self.download_timeout.setSuffix(" s")
        self.download_timeout.setValue(settings.download_timeout_seconds)
        download_form.addRow("Timeout de descarga", self.download_timeout)

        self.retries = QSpinBox()
        self.retries.setRange(0, 5)
        self.retries.setValue(settings.retries)
        download_form.addRow("Reintentos", self.retries)

        self.concurrency = QSpinBox()
        self.concurrency.setRange(1, 8)
        self.concurrency.setValue(settings.max_concurrent_downloads)
        download_form.addRow("Descargas simultáneas", self.concurrency)

        self.allow_any = QCheckBox("Permitir hosts distintos de Google Drive")
        self.allow_any.setChecked(settings.allow_any_host)
        download_form.addRow("", self.allow_any)
        downloads.content.addLayout(download_form)
        self.content.addWidget(downloads)

        appearance = Card()
        appearance_title = QLabel("Apariencia")
        appearance_title.setObjectName("SectionTitle")
        appearance.content.addWidget(appearance_title)
        appearance_form = QFormLayout()
        appearance_form.setContentsMargins(0, 2, 0, 2)
        appearance_form.setHorizontalSpacing(18)
        appearance_form.setVerticalSpacing(12)
        self.accent = QComboBox()
        for key in ACCENTS:
            self.accent.addItem(key.capitalize(), key)
        index = self.accent.findData(settings.accent)
        self.accent.setCurrentIndex(max(0, index))
        self.accent.currentIndexChanged.connect(
            lambda: self.accent_changed.emit(str(self.accent.currentData()))
        )
        appearance_form.addRow("Color de acento", self.accent)
        self.log_level = QComboBox()
        for level in ("DEBUG", "INFO", "WARNING", "ERROR"):
            self.log_level.addItem(level, level)
        index = self.log_level.findData(settings.log_level)
        self.log_level.setCurrentIndex(max(0, index))
        appearance_form.addRow("Nivel de log", self.log_level)
        appearance.content.addLayout(appearance_form)
        self.content.addWidget(appearance)

        self.status = QLabel("Los cambios se aplican al guardar.")
        self.status.setObjectName("Muted")
        self.content.addWidget(self.status)
        self.content.addStretch(1)

    def _save(self) -> None:
        settings = GuiSettings(
            profile_dir=Path(self.profile_field.text()),
            output_dir=Path(self.output_field.text()),
            login_timeout_seconds=self.login_timeout.value(),
            download_timeout_seconds=self.download_timeout.value(),
            retries=self.retries.value(),
            max_concurrent_downloads=self.concurrency.value(),
            allow_any_host=self.allow_any.isChecked(),
            accent=str(self.accent.currentData()),
            log_level=str(self.log_level.currentData()),
        )
        self.settings_saved.emit(settings)

    def set_status(self, message: str, *, error: bool = False) -> None:
        self.status.setText(message)
        self.status.setStyleSheet(
            "color: #fda4af;" if error else "color: #7f95b3;"
        )

    def set_settings(self, settings: GuiSettings) -> None:
        self.profile_field.setText(str(settings.profile_dir))
        self.output_field.setText(str(settings.output_dir))
        self.login_timeout.setValue(settings.login_timeout_seconds)
        self.download_timeout.setValue(settings.download_timeout_seconds)
        self.retries.setValue(settings.retries)
        self.concurrency.setValue(settings.max_concurrent_downloads)
        self.allow_any.setChecked(settings.allow_any_host)
        index = self.accent.findData(settings.accent)
        if index >= 0:
            self.accent.setCurrentIndex(index)
        index = self.log_level.findData(settings.log_level)
        if index >= 0:
            self.log_level.setCurrentIndex(index)
