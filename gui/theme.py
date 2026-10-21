from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QFontDatabase


@dataclass(frozen=True, slots=True)
class Accent:
    name: str
    primary: str
    secondary: str
    soft: str


ACCENTS: dict[str, Accent] = {
    "violet": Accent("violet", "#8b5cf6", "#22d3ee", "#a78bfa"),
    "cyan": Accent("cyan", "#22d3ee", "#6366f1", "#67e8f9"),
    "emerald": Accent("emerald", "#34d399", "#22d3ee", "#6ee7b7"),
    "amber": Accent("amber", "#fbbf24", "#fb7185", "#fcd34d"),
}

BASE_QSS = """
QWidget {
    color: #e6edf7;
    font-family: "__FONT__";
    font-size: 14px;
    outline: none;
}
QMainWindow, QWidget#AppShell {
    background: #070b12;
}
QFrame#Sidebar {
    background: #090f1a;
    border-right: 1px solid #17243a;
}
QFrame#TopBar {
    background: transparent;
}
QFrame#Card {
    background: #0d1624;
    border: 1px solid #1b2a41;
    border-radius: 18px;
}
QFrame#SubtleCard {
    background: #0a1321;
    border: 1px solid #16243a;
    border-radius: 14px;
}
QLabel#AppName {
    color: #f4f8ff;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.4px;
}
QLabel#AppTag {
    color: #7f95b3;
    font-size: 12px;
}
QLabel#Title {
    color: #f4f8ff;
    font-size: 30px;
    font-weight: 800;
}
QLabel#Subtitle {
    color: #8ba0bd;
    font-size: 14px;
}
QLabel#SectionTitle {
    color: #f4f8ff;
    font-size: 16px;
    font-weight: 700;
}
QLabel#Muted {
    color: #7f95b3;
}
QLabel#Tiny {
    color: #6f86a6;
    font-size: 11px;
}
QLabel#StatValue {
    color: #f4f8ff;
    font-size: 26px;
    font-weight: 800;
}
QLabel#StatCaption {
    color: #7f95b3;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
}
QLabel#HeroKicker {
    color: __ACCENT__;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.6px;
}
QLabel#HeroTitle {
    color: #f8fbff;
    font-size: 34px;
    font-weight: 800;
}
QLabel#HeroText {
    color: #a9bdd8;
    font-size: 14px;
}
QLabel#Pill {
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#Pill[tone="success"] {
    background: #0d2c24;
    color: #6ee7b7;
    border: 1px solid #1d5a48;
}
QLabel#Pill[tone="warning"] {
    background: #2d2410;
    color: #fcd34d;
    border: 1px solid #6b5217;
}
QLabel#Pill[tone="danger"] {
    background: #2d1218;
    color: #fda4af;
    border: 1px solid #6b2231;
}
QLabel#Pill[tone="info"] {
    background: #10243a;
    color: #7dd3fc;
    border: 1px solid #1e4f75;
}
QLabel#Pill[tone="muted"] {
    background: #111c2c;
    color: #8ba0bd;
    border: 1px solid #243551;
}
QPushButton {
    border: none;
    border-radius: 11px;
    padding: 9px 16px;
    font-weight: 600;
}
QPushButton#Primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 __ACCENT__, stop:1 __ACCENT2__);
    color: #071018;
}
QPushButton#Primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 __ACCENT_SOFT__, stop:1 __ACCENT2__);
}
QPushButton#Primary:pressed {
    padding-top: 10px;
    padding-bottom: 8px;
}
QPushButton#Primary:disabled {
    background: #1a2638;
    color: #5f748f;
}
QPushButton#Ghost {
    background: #101b2c;
    color: #cfe0f6;
    border: 1px solid #223552;
}
QPushButton#Ghost:hover {
    background: #152338;
    border: 1px solid __ACCENT__;
}
QPushButton#Ghost:pressed {
    background: #0d1726;
}
QPushButton#Danger {
    background: #2a1219;
    color: #fda4af;
    border: 1px solid #5c2230;
}
QPushButton#Danger:hover {
    background: #3a1721;
}
QPushButton#NavButton {
    text-align: left;
    padding: 11px 14px;
    border-radius: 12px;
    color: #8ba0bd;
    background: transparent;
    border-left: 3px solid transparent;
}
QPushButton#NavButton:hover {
    background: #101a2b;
    color: #e6edf7;
}
QPushButton#NavButton:checked {
    background: #12203a;
    color: #f4f8ff;
    border-left: 3px solid __ACCENT__;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #081120;
    border: 1px solid #223552;
    border-radius: 10px;
    padding: 9px 12px;
    color: #e6edf7;
    selection-background-color: __ACCENT__;
    selection-color: #071018;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid __ACCENT__;
}
QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {
    color: #5f748f;
    background: #0a101b;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background: #0d1624;
    border: 1px solid #223552;
    selection-background-color: #14223a;
    outline: none;
}
QCheckBox {
    color: #cfe0f6;
    spacing: 9px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid #2b4161;
    background: #081120;
}
QCheckBox::indicator:checked {
    background: __ACCENT__;
    border: 1px solid __ACCENT__;
}
QTableView {
    background: transparent;
    border: none;
    gridline-color: transparent;
    selection-background-color: #12203a;
    selection-color: #f4f8ff;
    alternate-background-color: #0b1422;
}
QHeaderView::section {
    background: transparent;
    color: #7188a8;
    border: none;
    padding: 10px 8px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
}
QTableCornerButton::section {
    background: transparent;
    border: none;
}
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #243651;
    min-height: 28px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #355074;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: #243651;
    min-width: 28px;
    border-radius: 5px;
}
QPlainTextEdit#Console {
    background: #060b13;
    border: 1px solid #17263c;
    border-radius: 14px;
    color: #a8c0dd;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    padding: 10px;
    selection-background-color: #1d3557;
}
QProgressBar {
    background: #0a1321;
    border: 1px solid #1b2a41;
    border-radius: 7px;
    text-align: center;
    color: #cfe0f6;
    font-size: 10px;
}
QProgressBar::chunk {
    border-radius: 6px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 __ACCENT__, stop:1 __ACCENT2__);
}
QToolTip {
    background: #0d1624;
    color: #e6edf7;
    border: 1px solid #2b4161;
    padding: 6px 8px;
    border-radius: 6px;
}
QMenu {
    background: #0d1624;
    border: 1px solid #223552;
    padding: 6px;
}
QMenu::item {
    padding: 7px 24px 7px 12px;
    border-radius: 6px;
}
QMenu::item:selected {
    background: #14223a;
}
QFrame#Divider {
    background: #17243a;
    max-height: 1px;
    border: none;
}
"""


def preferred_font_family() -> str:
    families = set(QFontDatabase.families())
    for candidate in (
        "Segoe UI Variable",
        "Segoe UI",
        "Inter",
        "SF Pro Display",
        "Helvetica Neue",
        "DejaVu Sans",
        "Noto Sans",
        "Arial",
    ):
        if candidate in families:
            return candidate
    return QFontDatabase.systemFont(QFontDatabase.GeneralFont).family()


def build_stylesheet(accent_name: str) -> str:
    accent = ACCENTS.get(accent_name, ACCENTS["violet"])
    return (
        BASE_QSS.replace("__FONT__", preferred_font_family())
        .replace("__ACCENT_SOFT__", accent.soft)
        .replace("__ACCENT2__", accent.secondary)
        .replace("__ACCENT__", accent.primary)
    )
