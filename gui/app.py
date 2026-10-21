from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from .main_window import MainWindow
from .settings import SettingsStore
from .theme import build_stylesheet, preferred_font_family
from .widgets import asset_path


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("gdrive-dl")
    app.setOrganizationName("lococoi")
    app.setStyle("Fusion")

    app.setFont(QFont(preferred_font_family(), 10))

    root = Path(__file__).resolve().parent.parent
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
    return app.exec()
