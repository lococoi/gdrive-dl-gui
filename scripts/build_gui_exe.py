from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


class BuildError(RuntimeError):
    pass


class YtDlpProvider:
    def __init__(self, *, upgrade: bool = True) -> None:
        self._upgrade = upgrade

    def ensure_latest(self) -> str:
        if self._upgrade:
            print("Installing the latest yt-dlp release from PyPI")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "--no-cache-dir",
                    "yt-dlp",
                ],
                check=True,
            )
        try:
            import yt_dlp.version
        except ImportError as exc:
            raise BuildError(
                "yt-dlp is not installed. Install requirements-dev.txt first."
            ) from exc
        version = yt_dlp.version.__version__
        print(f"Using yt-dlp {version}")
        return version


class PyInstallerBuilder:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._spec = root / "gdrive-dl-gui.spec"

    def build(self) -> Path:
        if not self._spec.is_file():
            raise BuildError(f"Missing PyInstaller spec: {self._spec}")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "PyInstaller",
                "--noconfirm",
                "--clean",
                str(self._spec),
            ],
            cwd=self._root,
            check=True,
        )
        executable = self._root / "dist" / (
            "gdrive-dl-gui.exe" if os.name == "nt" else "gdrive-dl-gui"
        )
        if not executable.is_file():
            raise BuildError(f"PyInstaller did not produce {executable}")
        return executable


class BuildApplication:
    def __init__(self, root: Path, *, upgrade_yt_dlp: bool = True) -> None:
        self._root = root
        self._upgrade_yt_dlp = upgrade_yt_dlp

    def run(self) -> Path:
        YtDlpProvider(upgrade=self._upgrade_yt_dlp).ensure_latest()
        executable = PyInstallerBuilder(self._root).build()
        size = executable.stat().st_size / (1024 * 1024)
        print(f"Built: {executable} ({size:.1f} MiB)")
        return executable


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the standalone gdrive-dl GUI for Windows."
    )
    parser.add_argument(
        "--skip-ytdlp-upgrade",
        action="store_true",
        help="Use the installed yt-dlp version instead of installing the latest.",
    )
    arguments = parser.parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    try:
        BuildApplication(
            root,
            upgrade_yt_dlp=not arguments.skip_ytdlp_upgrade,
        ).run()
    except (BuildError, subprocess.CalledProcessError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
