from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gui.settings import GuiSettings, SettingsStore


class SettingsTests(unittest.TestCase):
    def test_defaults_are_relative_to_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            settings = GuiSettings.defaults(root)
            self.assertEqual(settings.profile_dir, root / "chrome_profile")
            self.assertEqual(settings.output_dir, root / "downloads")
            self.assertEqual(settings.accent, "violet")

    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            store = SettingsStore(root / "settings.json", root)
            settings = GuiSettings(
                profile_dir=root / "profile",
                output_dir=root / "output",
                retries=4,
                max_concurrent_downloads=3,
                allow_any_host=True,
                accent="emerald",
            )
            store.save(settings)
            loaded = store.load()
            self.assertEqual(loaded.profile_dir, settings.profile_dir)
            self.assertEqual(loaded.output_dir, settings.output_dir)
            self.assertEqual(loaded.retries, 4)
            self.assertEqual(loaded.max_concurrent_downloads, 3)
            self.assertTrue(loaded.allow_any_host)
            self.assertEqual(loaded.accent, "emerald")

    def test_invalid_payload_falls_back(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "settings.json"
            path.write_text("{not json", encoding="utf-8")
            loaded = SettingsStore(path, root).load()
            self.assertEqual(loaded, GuiSettings.defaults(root))

    def test_unknown_accent_falls_back(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "settings.json"
            path.write_text(json.dumps({"accent": "unknown"}), encoding="utf-8")
            loaded = SettingsStore(path, root).load()
            self.assertEqual(loaded.accent, "violet")

    def test_overrides_map_to_core_config(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            settings = GuiSettings.defaults(root)
            overrides = settings.to_overrides()
            self.assertEqual(overrides.profile_dir, settings.profile_dir)
            self.assertEqual(overrides.download_timeout_seconds, 3600.0)
            self.assertEqual(overrides.retries, 2)


if __name__ == "__main__":
    unittest.main()
