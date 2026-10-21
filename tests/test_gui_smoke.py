from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from gui.settings import SettingsStore

APP = QApplication.instance() or QApplication([])


class GuiSmokeTests(unittest.TestCase):
    def test_window_builds_and_renders(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            store = SettingsStore(root / "settings.json", root)
            window = MainWindow(root, store)
            window.resize(1200, 760)
            window.show()
            QTest.qWait(350)
            self.assertEqual(window._stack.count(), 5)
            pixmap = window.grab()
            self.assertFalse(pixmap.isNull())
            self.assertGreater(pixmap.width(), 0)
            window.close()
            APP.processEvents()


if __name__ == "__main__":
    unittest.main()
