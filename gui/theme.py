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
    "violet": Accent("violet", "#8b5cf6", "#6366f1", "#a78bfa"),
    "blue": Accent("blue", "#3b82f6", "#06b6d4", "#60a5fa"),
    "emerald": Accent("emerald", "#10b981", "#14b8a6", "#6ee7b7"),
    "rose": Accent("rose", "#f43f5e", "#8b5cf6", "#fda4af"),
}

BASE_QSS = """
QWidget {
    color: #e9edf6;
    font-family: "__FONT__";
    font-size: 14px;
    outline: none;
}
QMainWindow, QWidget#AppShell {
    background: #08090d;
}
QFrame#Sidebar {
    background: #0a0b10;
    border: none;
}
QFrame#TopBar {
    background: transparent;
}
QFrame#Card {
    background: #0f1016;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 20px;
}
QFrame#SubtleCard {
    background: rgba(255, 255, 255, 0.028);
    border: 1px solid rgba(255, 255, 255, 0.045);
    border-radius: 14px;
}
QLabel#AppName {
    color: #f6f8fc;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.3px;
}
QLabel#AppTag {
    color: #71778a;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.8px;
}
QLabel#Title {
    color: #f6f8fc;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -0.5px;
}
QLabel#Subtitle {
    color: #858b9c;
    font-size: 14px;
}
QLabel#SectionTitle {
    color: #f1f4fa;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: -0.2px;
}
QLabel#Muted {
    color: #838a9c;
}
QLabel#Tiny {
    color: #656c7e;
    font-size: 11px;
}
QLabel#StatValue {
    color: #f6f8fc;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -0.6px;
}
QLabel#StatCaption {
    color: #71788a;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}
QLabel#HeroKicker {
    color: __ACCENT__;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
}
QLabel#HeroTitle {
    color: #f9fafc;
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -1px;
}
QLabel#HeroText {
    color: #9ba2b3;
    font-size: 14px;
}
QLabel#Pill {
    border: none;
    border-radius: 9px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#Pill[tone="success"] {
    background: rgba(52, 211, 153, 0.12);
    color: #9ff0c8;
}
QLabel#Pill[tone="warning"] {
    background: rgba(251, 191, 36, 0.12);
    color: #f8d67d;
}
QLabel#Pill[tone="danger"] {
    background: rgba(244, 63, 94, 0.12);
    color: #fda4af;
}
QLabel#Pill[tone="info"] {
    background: rgba(56, 189, 248, 0.12);
    color: #9adcf8;
}
QLabel#Pill[tone="muted"] {
    background: rgba(255, 255, 255, 0.055);
    color: #969daf;
}
QPushButton {
    border: none;
    border-radius: 11px;
    padding: 9px 16px;
    font-weight: 650;
}
QPushButton#Primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 __ACCENT__, stop:1 __ACCENT2__);
    color: #ffffff;
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
    background: rgba(255, 255, 255, 0.07);
    color: #646b7d;
}
QPushButton#Ghost {
    background: rgba(255, 255, 255, 0.045);
    color: #d4d9e4;
    border: none;
}
QPushButton#Ghost:hover {
    background: rgba(255, 255, 255, 0.085);
    color: #ffffff;
}
QPushButton#Ghost:pressed {
    background: rgba(255, 255, 255, 0.055);
}
QPushButton#Danger {
    background: rgba(244, 63, 94, 0.12);
    color: #fda4af;
    border: none;
}
QPushButton#Danger:hover {
    background: rgba(244, 63, 94, 0.18);
}
QPushButton#NavButton {
    text-align: left;
    padding: 11px 14px;
    border-radius: 11px;
    color: #858c9e;
    background: transparent;
    border: none;
    font-weight: 600;
}
QPushButton#NavButton:hover {
    background: rgba(255, 255, 255, 0.04);
    color: #dfe4ee;
}
QPushButton#NavButton:checked {
    background: rgba(255, 255, 255, 0.075);
    color: #ffffff;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #0a0b10;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 9px 12px;
    color: #e9edf6;
    selection-background-color: __ACCENT__;
    selection-color: #ffffff;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid rgba(255, 255, 255, 0.22);
}
QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {
    color: #5f6678;
    background: #0b0c11;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background: #111218;
    border: 1px solid rgba(255, 255, 255, 0.08);
    selection-background-color: rgba(255, 255, 255, 0.07);
    outline: none;
}
QCheckBox {
    color: #cfd4df;
    spacing: 9px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid rgba(255, 255, 255, 0.14);
    background: #0a0b10;
}
QCheckBox::indicator:checked {
    background: __ACCENT__;
    border: 1px solid rgba(255, 255, 255, 0.12);
}
QTableView {
    background: transparent;
    border: none;
    gridline-color: transparent;
    selection-background-color: rgba(255, 255, 255, 0.055);
    selection-color: #ffffff;
    alternate-background-color: rgba(255, 255, 255, 0.018);
}
QHeaderView::section {
    background: transparent;
    color: #6f7688;
    border: none;
    padding: 10px 8px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
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
    background: rgba(255, 255, 255, 0.12);
    min-height: 28px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.2);
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
    background: rgba(255, 255, 255, 0.12);
    min-width: 28px;
    border-radius: 5px;
}
QPlainTextEdit#Console {
    background: #08090d;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    color: #a7aebe;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    padding: 10px;
    selection-background-color: rgba(255, 255, 255, 0.12);
}
QProgressBar {
    background: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 7px;
    text-align: center;
    color: #cfd4df;
    font-size: 10px;
}
QProgressBar::chunk {
    border-radius: 6px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 __ACCENT__, stop:1 __ACCENT2__);
}
QToolTip {
    background: #111218;
    color: #e9edf6;
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 6px 8px;
    border-radius: 6px;
}
QMenu {
    background: #111218;
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 6px;
}
QMenu::item {
    padding: 7px 24px 7px 12px;
    border-radius: 6px;
}
QMenu::item:selected {
    background: rgba(255, 255, 255, 0.07);
}
QFrame#Divider {
    background: rgba(255, 255, 255, 0.06);
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
