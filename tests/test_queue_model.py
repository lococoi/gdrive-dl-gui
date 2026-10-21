from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from gdrive_dl.errors import DownloadError
from gdrive_dl.models import DownloadResult
from gdrive_dl.models import DownloadStatus as CoreStatus
from gui.models import DownloadQueueModel, DownloadStatus

APP = QApplication.instance() or QApplication([])


class QueueModelTests(unittest.TestCase):
    def test_lifecycle(self) -> None:
        model = DownloadQueueModel()
        identifier = model.add_item("https://drive.google.com/file/d/abc/view")
        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(model.stats().queued, 1)

        model.start_item(identifier)
        self.assertEqual(model.items[0].status, DownloadStatus.RUNNING)

        model.finish_item(
            identifier,
            DownloadResult(
                status=CoreStatus.DOWNLOADED,
                url="https://drive.google.com/file/d/abc/view",
                output_path=None,
                attempts=2,
                duration_seconds=3.5,
                message="ok",
            ),
        )
        item = model.items[0]
        self.assertEqual(item.status, DownloadStatus.COMPLETED)
        self.assertEqual(item.attempts, 2)
        self.assertEqual(model.stats().finished, 1)

        model.clear_finished()
        self.assertEqual(model.rowCount(), 0)

    def test_failure_message_includes_hint(self) -> None:
        model = DownloadQueueModel()
        identifier = model.add_item("bad")
        model.fail_item(identifier, DownloadError("falló", hint="revisa"))
        item = model.items[0]
        self.assertEqual(item.status, DownloadStatus.FAILED)
        self.assertIn("revisa", item.message)


if __name__ == "__main__":
    unittest.main()
