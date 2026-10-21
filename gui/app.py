from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from .main_window import MainWindow
from .settings import SettingsStore
from .theme import build_stylesheet, preferred_font_family
from .widgets import asset_path


def application_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def main() -> int:
    smoke_test = "--smoke-test" in sys.argv
    if smoke_test:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"

    app = QApplication([argument for argument in sys.argv if argument != "--smoke-test"])
    app.setApplicationName("gdrive-dl")
    app.setOrganizationName("lococoi")
    app.setStyle("Fusion")
    app.setFont(QFont(preferred_font_family(), 10))

    root = application_root()
    store = SettingsStore(root / "settings.json", root)
    settings = store.load()
    app.setWindowIcon(QIcon(str(asset_path("logo.ico"))))
    app.setStyleSheet(build_stylesheet(settings.accent))

    try:
        window = MainWindow(root, store)
    except Exception as exc:
        QMessageBox.critical(
            None,
            "gdrive-dl",
            f"No se pudo iniciar la aplicación:\n{exc}",
        )
        return 1

    window.show()
    if smoke_test:
        QTimer.singleShot(800, window.close)
        QTimer.singleShot(2400, app.quit)
    return app.exec()
