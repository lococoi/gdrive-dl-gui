from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from gdrive_dl.config import ConfigOverrides

from .theme import ACCENTS


@dataclass(slots=True)
class GuiSettings:
    profile_dir: Path
    output_dir: Path
    login_timeout_seconds: float = 900.0
    download_timeout_seconds: float = 3600.0
    retries: int = 2
    max_concurrent_downloads: int = 2
    allow_any_host: bool = False
    accent: str = "violet"
    log_level: str = "INFO"

    @classmethod
    def defaults(cls, root: Path) -> GuiSettings:
        return cls(
            profile_dir=root / "chrome_profile",
            output_dir=root / "downloads",
        )

    @classmethod
    def from_payload(cls, payload: dict[str, Any], root: Path) -> GuiSettings:
        defaults = cls.defaults(root)
        accent = str(payload.get("accent", defaults.accent))
        if accent not in ACCENTS:
            accent = defaults.accent
        try:
            return cls(
                profile_dir=Path(payload.get("profile_dir", defaults.profile_dir)),
                output_dir=Path(payload.get("output_dir", defaults.output_dir)),
                login_timeout_seconds=float(
                    payload.get("login_timeout_seconds", defaults.login_timeout_seconds)
                ),
                download_timeout_seconds=float(
                    payload.get(
                        "download_timeout_seconds",
                        defaults.download_timeout_seconds,
                    )
                ),
                retries=int(payload.get("retries", defaults.retries)),
                max_concurrent_downloads=int(
                    payload.get(
                        "max_concurrent_downloads",
                        defaults.max_concurrent_downloads,
                    )
                ),
                allow_any_host=bool(
                    payload.get("allow_any_host", defaults.allow_any_host)
                ),
                accent=accent,
                log_level=str(payload.get("log_level", defaults.log_level)),
            )
        except (TypeError, ValueError):
            return defaults

    def to_overrides(self) -> ConfigOverrides:
        return ConfigOverrides(
            profile_dir=self.profile_dir,
            output_dir=self.output_dir,
            login_timeout_seconds=self.login_timeout_seconds,
            download_timeout_seconds=self.download_timeout_seconds,
            max_concurrent_downloads=self.max_concurrent_downloads,
            retries=self.retries,
            allow_any_host=self.allow_any_host,
            log_level=self.log_level,
        )

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["profile_dir"] = str(self.profile_dir)
        payload["output_dir"] = str(self.output_dir)
        return payload


class SettingsStore:
    def __init__(self, path: Path, root: Path) -> None:
        self._path = path
        self._root = root

    def load(self) -> GuiSettings:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return GuiSettings.defaults(self._root)
        if not isinstance(payload, dict):
            return GuiSettings.defaults(self._root)
        return GuiSettings.from_payload(payload, self._root)

    def save(self, settings: GuiSettings) -> None:
        temporary = self._path.with_suffix(".json.tmp")
        try:
            temporary.write_text(
                json.dumps(settings.to_payload(), indent=2),
                encoding="utf-8",
            )
            temporary.replace(self._path)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise
