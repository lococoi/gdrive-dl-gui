from __future__ import annotations

import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from gdrive_dl.config import ConfigFactory
from gdrive_dl.container import ContainerFactory, ServiceContainer
from gdrive_dl.errors import GdriveError
from gdrive_dl.infrastructure.logging import LoggingConfigurator
from gdrive_dl.models import DoctorReport, DownloadResult, SystemStatus
from gdrive_dl.ports import ProgressReporter

from .settings import GuiSettings


class ProgressBridge(QObject):
    line = Signal(str)


class SignalProgressReporter(ProgressReporter):
    def __init__(self, bridge: ProgressBridge) -> None:
        self._bridge = bridge

    @property
    def enabled(self) -> bool:
        return True

    def report(self, line: str) -> None:
        self._bridge.line.emit(line.rstrip())


class BridgeLogHandler(logging.Handler):
    def __init__(self, bridge: ProgressBridge) -> None:
        super().__init__()
        self._bridge = bridge
        self.setFormatter(logging.Formatter("%(levelname)s  %(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._bridge.line.emit(self.format(record))
        except Exception:
            self.handleError(record)


class WorkerSignals(QObject):
    started = Signal()
    finished = Signal(object)
    failed = Signal(object)


class TaskWorker(QRunnable):
    def __init__(self, function: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self._function = function
        self._args = args
        self._kwargs = kwargs
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    @Slot()
    def run(self) -> None:
        self.signals.started.emit()
        try:
            result = self._function(*self._args, **self._kwargs)
        except GdriveError as exc:
            self.signals.failed.emit(exc)
        except Exception as exc:
            self.signals.failed.emit(exc)
        else:
            self.signals.finished.emit(result)


class GuiBackend:
    def __init__(
        self,
        root: Path,
        settings: GuiSettings,
        bridge: ProgressBridge,
    ) -> None:
        self._root = root
        self._bridge = bridge
        self._settings = settings
        self._config = None
        self._container: ServiceContainer | None = None
        self._logger = logging.getLogger("gdrive_dl")
        self._rebuild(settings)

    @property
    def config(self):
        return self._config

    @property
    def container(self) -> ServiceContainer:
        if self._container is None:
            raise RuntimeError("Backend is not initialized")
        return self._container

    def update_settings(self, settings: GuiSettings) -> None:
        self._rebuild(settings)

    def _rebuild(self, settings: GuiSettings) -> None:
        config = ConfigFactory(self._root, os.environ).create(settings.to_overrides())
        logger = LoggingConfigurator(config).configure()
        logger.addHandler(BridgeLogHandler(self._bridge))
        factory = ContainerFactory(config, logger, os.environ)
        self._config = config
        self._container = factory.create(SignalProgressReporter(self._bridge))
        self._settings = settings
        self._logger = logger

    def login(self):
        return self.container.login_service.login()

    def download(self, url: str) -> DownloadResult:
        return self.container.download_service.download(url)

    def status(self) -> SystemStatus:
        return self.container.status_service.snapshot()

    def doctor(self) -> DoctorReport:
        return self.container.doctor_service.run()

    def close(self) -> None:
        LoggingConfigurator.close()
