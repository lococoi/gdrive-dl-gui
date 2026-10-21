from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool, QTimer, QUrl
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QIcon,
    QKeySequence,
    QPainter,
    QRadialGradient,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gdrive_dl.errors import GdriveError
from gdrive_dl.models import DoctorReport, DownloadResult, SystemStatus

from .models import DownloadQueueModel
from .pages import (
    DiagnosticsPage,
    DownloadsPage,
    OverviewPage,
    SessionPage,
    SettingsPage,
)
from .settings import GuiSettings, SettingsStore
from .theme import ACCENTS, build_stylesheet
from .widgets import (
    AnimatedStack,
    SidebarButton,
    StatusPill,
    Toast,
    asset_path,
)
from .workers import GuiBackend, ProgressBridge, TaskWorker

PAGE_META = (
    ("Resumen", "Sesión, actividad y accesos rápidos"),
    ("Descargas", "Cola dinámica y resultados"),
    ("Sesión", "Perfil aislado de Chrome"),
    ("Diagnóstico", "Comprobaciones del entorno"),
    ("Ajustes", "Rutas, concurrencia y apariencia"),
)


class AppShell(QWidget):
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor("#070b12"))

        painter.setPen(QColor(255, 255, 255, 14))
        spacing = 30
        for x in range(0, self.width(), spacing):
            for y in range(0, self.height(), spacing):
                painter.drawPoint(x, y)

        glow = QRadialGradient(self.width() * 0.8, -40, self.width() * 0.55)
        glow.setColorAt(0.0, QColor(34, 211, 238, 28))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), glow)

        glow2 = QRadialGradient(-40, self.height() * 0.25, self.width() * 0.5)
        glow2.setColorAt(0.0, QColor(139, 92, 246, 24))
        glow2.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), glow2)


class MainWindow(QMainWindow):
    def __init__(self, root: Path, settings_store: SettingsStore) -> None:
        super().__init__()
        self._root = root
        self._settings_store = settings_store
        self._settings = settings_store.load()
        self._bridge = ProgressBridge()
        self._bridge.line.connect(self._on_log_line)
        self._backend = GuiBackend(root, self._settings, self._bridge)
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(self._settings.max_concurrent_downloads)
        self._workers: set[TaskWorker] = set()
        self._status_busy = False
        self._login_busy = False
        self._doctor_busy = False
        self._active_accent = self._settings.accent

        self.setWindowTitle("gdrive-dl")
        self.setWindowIcon(QIcon(str(asset_path("logo.ico"))))
        self.setMinimumSize(1120, 720)
        self.resize(1360, 860)
        self.setAcceptDrops(True)

        self._model = DownloadQueueModel()
        self._overview = OverviewPage()
        self._downloads = DownloadsPage(self._model)
        self._session = SessionPage()
        self._diagnostics = DiagnosticsPage()
        self._settings_page = SettingsPage(self._settings)

        shell = AppShell()
        self.setCentralWidget(shell)
        root_layout = QHBoxLayout(shell)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._build_sidebar())

        main_area = QWidget()
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(18)
        main_layout.addWidget(self._build_header())

        self._stack = AnimatedStack()
        for page in (
            self._overview,
            self._downloads,
            self._session,
            self._diagnostics,
            self._settings_page,
        ):
            self._stack.addWidget(page)
        main_layout.addWidget(self._stack, 1)
        root_layout.addWidget(main_area, 1)

        self._toast = Toast(shell)
        self._wire_events()
        self._apply_accent(self._settings.accent)
        self._refresh_queue_views()
        self._navigate(0)

        self._phase_timer = QTimer(self)
        self._phase_timer.setInterval(70)
        self._phase_timer.timeout.connect(self._model.bump_phase)
        self._phase_timer.start()

        self._status_timer = QTimer(self)
        self._status_timer.setInterval(12000)
        self._status_timer.timeout.connect(self.refresh_status)
        self._status_timer.start()

        QTimer.singleShot(120, self.refresh_status)

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(250)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 20)
        layout.setSpacing(8)

        brand = QHBoxLayout()
        brand.setSpacing(10)
        logo = QLabel()
        logo.setPixmap(
            QIcon(str(asset_path("logo.ico"))).pixmap(40, 40)
        )
        logo.setFixedSize(40, 40)
        brand.addWidget(logo)
        names = QVBoxLayout()
        names.setSpacing(0)
        name = QLabel("gdrive-dl")
        name.setObjectName("AppName")
        tag = QLabel("CONTROL CENTER")
        tag.setObjectName("AppTag")
        names.addWidget(name)
        names.addWidget(tag)
        brand.addLayout(names)
        layout.addLayout(brand)
        layout.addSpacing(18)

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)
        self._nav_buttons: list[SidebarButton] = []
        for index, (title, _) in enumerate(PAGE_META):
            button = SidebarButton(title)
            button.clicked.connect(lambda checked=False, i=index: self._navigate(i))
            self._nav_group.addButton(button, index)
            self._nav_buttons.append(button)
            layout.addWidget(button)
        layout.addStretch(1)

        divider = QFrame()
        divider.setObjectName("Divider")
        layout.addWidget(divider)
        layout.addSpacing(6)

        status_card = QFrame()
        status_card.setObjectName("SubtleCard")
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(12, 12, 12, 12)
        status_layout.setSpacing(7)
        status_caption = QLabel("ESTADO")
        status_caption.setObjectName("StatCaption")
        status_layout.addWidget(status_caption)
        self._sidebar_pill = StatusPill("Verificando", "muted")
        status_layout.addWidget(self._sidebar_pill)
        self._sidebar_detail = QLabel("Comprobando entorno…")
        self._sidebar_detail.setObjectName("Tiny")
        self._sidebar_detail.setWordWrap(True)
        status_layout.addWidget(self._sidebar_detail)
        layout.addWidget(status_card)
        layout.addSpacing(8)

        version = QLabel(f"v{self._version()}")
        version.setObjectName("Tiny")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        return sidebar

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("TopBar")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(14)
        titles = QVBoxLayout()
        titles.setSpacing(2)
        self._title = QLabel(PAGE_META[0][0])
        self._title.setObjectName("Title")
        self._subtitle = QLabel(PAGE_META[0][1])
        self._subtitle.setObjectName("Subtitle")
        titles.addWidget(self._title)
        titles.addWidget(self._subtitle)
        layout.addLayout(titles, 1)
        self._header_pill = StatusPill("Comprobando", "muted")
        layout.addWidget(self._header_pill)
        self._refresh_button = QPushButton("Actualizar")
        self._refresh_button.setObjectName("Ghost")
        self._refresh_button.clicked.connect(self.refresh_status)
        layout.addWidget(self._refresh_button)
        return header

    def _wire_events(self) -> None:
        self._overview.download_requested.connect(self.enqueue_download)
        self._overview.login_requested.connect(self.run_login)
        self._overview.doctor_requested.connect(self.run_doctor)
        self._overview.open_output_requested.connect(self.open_output)
        self._overview.refresh_button.clicked.connect(self.refresh_status)

        self._downloads.clear_requested.connect(self._clear_finished)
        self._downloads.open_requested.connect(self.open_output)
        self._downloads.reveal_requested.connect(self._reveal_path)

        self._session.login_requested.connect(self.run_login)
        self._session.refresh_requested.connect(self.refresh_status)
        self._session.open_profile_requested.connect(self.open_profile)

        self._diagnostics.run_requested.connect(self.run_doctor)
        self._settings_page.settings_saved.connect(self.apply_settings)
        self._settings_page.accent_changed.connect(self._apply_accent)

        self._model.rowsInserted.connect(self._refresh_queue_views)
        self._model.rowsRemoved.connect(self._refresh_queue_views)
        self._model.modelReset.connect(self._refresh_queue_views)
        self._model.dataChanged.connect(self._refresh_queue_views)

        paste = QShortcut(QKeySequence("Ctrl+V"), self)
        paste.activated.connect(self._paste_url)
        refresh = QShortcut(QKeySequence("F5"), self)
        refresh.activated.connect(self.refresh_status)
        login = QShortcut(QKeySequence("Ctrl+L"), self)
        login.activated.connect(self.run_login)
        download = QShortcut(QKeySequence("Ctrl+Return"), self)
        download.activated.connect(self._download_from_hero)

    def _navigate(self, index: int) -> None:
        self._stack.set_current(index)
        title, subtitle = PAGE_META[index]
        self._title.setText(title)
        self._subtitle.setText(subtitle)
        if 0 <= index < len(self._nav_buttons):
            self._nav_buttons[index].setChecked(True)
        if index == 2:
            self.refresh_status()

    def enqueue_download(self, url: str) -> None:
        cleaned = url.strip()
        if not cleaned:
            self._toast.show_message("Pega un enlace primero.", "warning")
            return
        identifier = self._model.add_item(cleaned)
        worker = TaskWorker(self._backend.download, cleaned)
        worker.signals.started.connect(
            lambda: self._model.start_item(identifier)
        )
        worker.signals.finished.connect(
            lambda result: self._on_download_finished(identifier, result)
        )
        worker.signals.failed.connect(
            lambda exc: self._on_download_failed(identifier, exc)
        )
        self._start_worker(worker)
        self._overview.clear_url()
        self._refresh_queue_views()
        self._toast.show_message("Descarga añadida a la cola.", "info")

    def _on_download_finished(self, identifier: int, result: object) -> None:
        if isinstance(result, DownloadResult):
            self._model.finish_item(identifier, result)
            tone = (
                "warning"
                if result.status.value == "skipped"
                else "success"
            )
            message = result.message or "Descarga completada."
            if result.output_path:
                message = f"{message} · {result.output_path.name}"
            self._toast.show_message(message, tone, 4200)
        self._refresh_queue_views()

    def _on_download_failed(self, identifier: int, exc: object) -> None:
        error = exc if isinstance(exc, BaseException) else RuntimeError(str(exc))
        self._model.fail_item(identifier, error)
        self._toast.show_message(str(error), "danger", 5200)
        self._refresh_queue_views()

    def _start_worker(self, worker: TaskWorker) -> None:
        self._workers.add(worker)
        worker.signals.finished.connect(lambda _: self._workers.discard(worker))
        worker.signals.failed.connect(lambda _: self._workers.discard(worker))
        self._pool.start(worker)

    def refresh_status(self) -> None:
        if self._status_busy:
            return
        self._status_busy = True
        self._refresh_button.setDisabled(True)
        worker = TaskWorker(self._backend.status)
        worker.signals.finished.connect(self._on_status_ready)
        worker.signals.failed.connect(self._on_status_failed)
        self._start_worker(worker)

    def _on_status_ready(self, result: object) -> None:
        self._status_busy = False
        self._refresh_button.setDisabled(False)
        if not isinstance(result, SystemStatus):
            return
        self._overview.set_status(result)
        self._session.set_status(result)
        session = result.session
        if session.available:
            self._header_pill.set_state("Sesión activa", "success")
            self._sidebar_pill.set_state("Operativo", "success")
            self._sidebar_detail.setText(
                f"{session.google_auth_cookie_count} cookies · "
                f"yt-dlp {result.yt_dlp_version or '—'}"
            )
        else:
            self._header_pill.set_state("Sin sesión", "warning")
            self._sidebar_pill.set_state("Requiere login", "warning")
            self._sidebar_detail.setText(session.reason or "Ejecuta login.")
        self._refresh_queue_views()

    def _on_status_failed(self, exc: object) -> None:
        self._status_busy = False
        self._refresh_button.setDisabled(False)
        self._header_pill.set_state("Error de estado", "danger")
        self._sidebar_pill.set_state("Error", "danger")
        self._sidebar_detail.setText(str(exc))

    def run_login(self) -> None:
        if self._login_busy:
            return
        self._login_busy = True
        self._overview.set_login_busy(True)
        self._session.set_busy(True)
        self._toast.show_message("Abriendo Chrome. Completa el login.", "info", 5000)
        worker = TaskWorker(self._backend.login)
        worker.signals.finished.connect(self._on_login_finished)
        worker.signals.failed.connect(self._on_login_failed)
        self._start_worker(worker)

    def _on_login_finished(self, result: object) -> None:
        self._login_busy = False
        self._overview.set_login_busy(False)
        self._session.set_busy(False)
        self._toast.show_message("Sesión verificada correctamente.", "success")
        self.refresh_status()

    def _on_login_failed(self, exc: object) -> None:
        self._login_busy = False
        self._overview.set_login_busy(False)
        self._session.set_busy(False)
        self._toast.show_message(str(exc), "danger", 6000)
        self.refresh_status()

    def run_doctor(self) -> None:
        if self._doctor_busy:
            return
        self._doctor_busy = True
        self._navigate(3)
        self._diagnostics.set_busy(True)
        worker = TaskWorker(self._backend.doctor)
        worker.signals.finished.connect(self._on_doctor_finished)
        worker.signals.failed.connect(self._on_doctor_failed)
        self._start_worker(worker)

    def _on_doctor_finished(self, result: object) -> None:
        self._doctor_busy = False
        self._diagnostics.set_busy(False)
        if isinstance(result, DoctorReport):
            self._diagnostics.set_report(result)
            tone = "success" if result.healthy else "warning"
            text = "Diagnóstico completado." if result.healthy else "Hay comprobaciones pendientes."
            self._toast.show_message(text, tone)

    def _on_doctor_failed(self, exc: object) -> None:
        self._doctor_busy = False
        self._diagnostics.set_busy(False)
        self._toast.show_message(str(exc), "danger", 6000)

    def apply_settings(self, settings: GuiSettings) -> None:
        try:
            self._backend.update_settings(settings)
        except (GdriveError, OSError, ValueError) as exc:
            self._settings_page.set_status(str(exc), error=True)
            self._toast.show_message(str(exc), "danger", 6000)
            return
        self._settings = settings
        try:
            self._settings_store.save(settings)
        except OSError as exc:
            self._settings_page.set_status(str(exc), error=True)
            self._toast.show_message(f"No se pudo guardar la configuración: {exc}", "danger")
            return
        self._pool.setMaxThreadCount(settings.max_concurrent_downloads)
        self._apply_accent(settings.accent)
        self._settings_page.set_status("Cambios guardados.")
        self._toast.show_message("Configuración aplicada.", "success")
        self.refresh_status()

    def _apply_accent(self, name: str) -> None:
        accent = ACCENTS.get(name, ACCENTS["violet"])
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(build_stylesheet(accent.name))
        self._overview.set_accent(accent.name)
        self._active_accent = accent.name

    def _clear_finished(self) -> None:
        self._model.clear_finished()
        self._refresh_queue_views()

    def _refresh_queue_views(self) -> None:
        stats = self._model.stats()
        self._overview.set_queue_stats(stats)
        self._downloads.set_stats(stats)
        self._overview.set_recent(self._model.items)

    def open_output(self) -> None:
        path = self._backend.config.output_dir
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self._toast.show_message(str(exc), "danger")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def open_profile(self) -> None:
        path = self._backend.config.profile_dir
        if not path.exists():
            self._toast.show_message("El perfil todavía no existe.", "warning")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _reveal_path(self, path: Path) -> None:
        target = path if path.exists() else path.parent
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    def _paste_url(self) -> None:
        clipboard = QApplication.clipboard().text().strip()
        if not clipboard:
            return
        self._navigate(0)
        self._overview.hero.url_input.setText(clipboard)
        self._overview.hero.url_input.setFocus()

    def _download_from_hero(self) -> None:
        self.enqueue_download(self._overview.take_url())

    def _on_log_line(self, line: str) -> None:
        self._overview.append_log(line)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        accepted = False
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.scheme() in {"http", "https"}:
                    self.enqueue_download(url.toString())
                    accepted = True
        elif event.mimeData().hasText():
            self.enqueue_download(event.mimeData().text())
            accepted = True
        if accepted:
            event.acceptProposedAction()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "_toast"):
            self._toast._reposition()

    def closeEvent(self, event) -> None:
        self._phase_timer.stop()
        self._status_timer.stop()
        self._pool.clear()
        self._pool.waitForDone(1500)
        self._backend.close()
        super().closeEvent(event)

    @staticmethod
    def _version() -> str:
        from . import __version__

        return __version__
