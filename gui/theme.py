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
    "violet": Accent("violet", "#6d5ef7", "#ff7a59", "#9b8cff"),
    "blue": Accent("blue", "#2563eb", "#06b6d4", "#60a5fa"),
    "emerald": Accent("emerald", "#059669", "#14b8a6", "#34d399"),
    "rose": Accent("rose", "#e11d48", "#f97316", "#fb7185"),
}

BASE_QSS = """
QWidget {
    color: #111114;
    font-family: "__FONT__";
    font-size: 14px;
    outline: none;
}
QMainWindow, QWidget#AppShell {
    background: #f4f1ea;
}
QFrame#TopBar {
    background: transparent;
}
QFrame#Card {
    background: #ffffff;
    border: none;
    border-radius: 24px;
}
QFrame#SubtleCard {
    background: #f7f4ed;
    border: none;
    border-radius: 18px;
}
QFrame#DarkCard {
    background: #131316;
    border: none;
    border-radius: 24px;
}
QFrame#SearchCard {
    background: #ffffff;
    border: none;
    border-radius: 18px;
}
QLabel#AppName {
    color: #111114;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.4px;
}
QLabel#AppTag {
    color: #8a8377;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.4px;
}
QLabel#Title {
    color: #111114;
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -1px;
}
QLabel#Subtitle {
    color: #6f6a61;
    font-size: 14px;
}
QLabel#SectionTitle {
    color: #111114;
    font-size: 20px;
    font-weight: 750;
    letter-spacing: -0.4px;
}
QLabel#Muted {
    color: #6f6a61;
}
QLabel#Tiny {
    color: #928c80;
    font-size: 11px;
}
QLabel#Footer {
    color: #928c80;
    font-size: 12px;
}
QLabel#StatValue {
    color: #111114;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -1px;
}
QLabel#StatCaption {
    color: #8a8377;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.1px;
}
QLabel#HeroKicker {
    color: __ACCENT__;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.8px;
}
QLabel#HeroTitle {
    color: #111114;
    font-size: 52px;
    font-weight: 800;
    letter-spacing: -2px;
}
QLabel#HeroText {
    color: #5f5a52;
    font-size: 16px;
}
QLabel#Pill {
    border: none;
    border-radius: 999px;
    padding: 6px 12px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#Pill[tone="success"] {
    background: #dcfce7;
    color: #166534;
}
QLabel#Pill[tone="warning"] {
    background: #fef3c7;
    color: #92400e;
}
QLabel#Pill[tone="danger"] {
    background: #fee2e2;
    color: #991b1b;
}
QLabel#Pill[tone="info"] {
    background: #e0e7ff;
    color: #3730a3;
}
QLabel#Pill[tone="muted"] {
    background: #ece8df;
    color: #6b6459;
}
QPushButton {
    border: none;
    border-radius: 999px;
    padding: 10px 18px;
    font-weight: 650;
}
QPushButton#Primary {
    background: #111114;
    color: #ffffff;
}
QPushButton#Primary:hover {
    background: #2a2a30;
}
QPushButton#Primary:pressed {
    background: #000000;
}
QPushButton#Primary:disabled {
    background: #ddd7cb;
    color: #8a8377;
}
QPushButton#Ghost {
    background: #efece5;
    color: #111114;
}
QPushButton#Ghost:hover {
    background: #e7e2d8;
}
QPushButton#Ghost:pressed {
    background: #ded8cc;
}
QPushButton#Danger {
    background: #fee2e2;
    color: #991b1b;
}
QPushButton#Danger:hover {
    background: #fecaca;
}
QPushButton#NavButton {
    text-align: center;
    padding: 8px 14px;
    border-radius: 999px;
    color: #6f6a61;
    background: transparent;
    border: none;
    font-weight: 650;
}
QPushButton#NavButton:hover {
    background: #ede8dd;
    color: #111114;
}
QPushButton#NavButton:checked {
    background: #111114;
    color: #ffffff;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #f4f1ea;
    border: none;
    border-radius: 12px;
    padding: 11px 14px;
    color: #111114;
    selection-background-color: #111114;
    selection-color: #ffffff;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    background: #ece7dc;
}
QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {
    color: #9a9488;
    background: #f1eee7;
}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    width: 0;
    border: none;
    background: transparent;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
    background: transparent;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    border: none;
    selection-background-color: #f0ece3;
    outline: none;
}
QCheckBox {
    color: #3f3b35;
    spacing: 9px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: none;
    background: #e9e4d9;
}
QCheckBox::indicator:checked {
    background: #111114;
}
QTableView {
    background: transparent;
    border: none;
    gridline-color: transparent;
    selection-background-color: #f0ece3;
    selection-color: #111114;
    alternate-background-color: #faf7f0;
}
QHeaderView::section {
    background: transparent;
    color: #8a8377;
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
    background: #d8d1c4;
    min-height: 28px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #c8c0b1;
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
    background: #d8d1c4;
    min-width: 28px;
    border-radius: 5px;
}
QPlainTextEdit#Console {
    background: #131316;
    border: none;
    border-radius: 18px;
    color: #e8e4dc;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    padding: 12px;
    selection-background-color: #3a3845;
}
QProgressBar {
    background: #e9e3d8;
    border: none;
    border-radius: 999px;
    text-align: center;
    color: #5f5a52;
    font-size: 10px;
}
QProgressBar::chunk {
    border-radius: 999px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 __ACCENT__, stop:1 __ACCENT2__);
}
QToolTip {
    background: #111114;
    color: #f7f4ed;
    border: none;
    padding: 6px 8px;
    border-radius: 6px;
}
QMenu {
    background: #ffffff;
    border: none;
    padding: 6px;
}
QMenu::item {
    padding: 7px 24px 7px 12px;
    border-radius: 7px;
}
QMenu::item:selected {
    background: #f0ece3;
}
"""


def preferred_font_family() -> str:
    families = set(QFontDatabase.families())
    for candidate in (
        "Segoe UI Variable Display",
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
