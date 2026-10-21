from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
    QRadialGradient,
    QTextCharFormat,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def asset_path(name: str) -> Path:
    return ASSETS / name


class Card(QFrame):
    def __init__(self, parent: QWidget | None = None, *, subtle: bool = False) -> None:
        super().__init__(parent)
        self.setObjectName("SubtleCard" if subtle else "Card")
        self._content = QVBoxLayout(self)
        self._content.setContentsMargins(20, 20, 20, 20)
        self._content.setSpacing(12)

    @property
    def content(self) -> QVBoxLayout:
        return self._content


class StatCard(Card):
    def __init__(
        self,
        caption: str,
        value: str = "—",
        accent: str = "#8b5cf6",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setMinimumHeight(96)
        self._accent = accent
        top = QHBoxLayout()
        top.setSpacing(8)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {accent}; border-radius: 4px;")
        top.addWidget(dot)
        top.addWidget(self._caption_label(caption))
        top.addStretch(1)
        self.content.addLayout(top)
        self._value = QLabel(value)
        self._value.setObjectName("StatValue")
        self.content.addWidget(self._value)
        self._detail = QLabel("")
        self._detail.setObjectName("Muted")
        self.content.addWidget(self._detail)

    @staticmethod
    def _caption_label(text: str) -> QLabel:
        label = QLabel(text.upper())
        label.setObjectName("StatCaption")
        return label

    def set_value(self, value: str, detail: str = "") -> None:
        self._value.setText(value)
        self._detail.setText(detail)


class StatusPill(QLabel):
    def __init__(self, text: str = "", tone: str = "muted") -> None:
        super().__init__(text)
        self.setObjectName("Pill")
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.set_state(text, tone)

    def set_state(self, text: str, tone: str) -> None:
        self.setText(text)
        self.setProperty("tone", tone)
        self.style().unpolish(self)
        self.style().polish(self)


class SidebarButton(QPushButton):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setObjectName("NavButton")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(42)


class HeroCard(QFrame):
    download_requested = Signal(str)

    def __init__(self, accent: QColor, accent_secondary: QColor) -> None:
        super().__init__()
        self.setObjectName("HeroCard")
        self.setMinimumHeight(262)
        self._accent = accent
        self._accent_secondary = accent_secondary
        self._phase = 0.0
        self._logo = QPixmap(str(asset_path("logo.png")))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 28, 30, 28)
        layout.setSpacing(10)

        kicker = QLabel("GOOGLE DRIVE · SESIÓN AISLADA")
        kicker.setObjectName("HeroKicker")
        layout.addWidget(kicker)

        title = QLabel("Descarga sin fricción.")
        title.setObjectName("HeroTitle")
        layout.addWidget(title)

        text = QLabel(
            "Pega un enlace de Google Drive. La sesión vive en un perfil de "
            "Chrome separado y las descargas se ejecutan con timeouts y reintentos."
        )
        text.setObjectName("HeroText")
        text.setWordWrap(True)
        layout.addWidget(text)
        layout.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(10)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://drive.google.com/file/d/…/view")
        self.url_input.setMinimumHeight(44)
        self.url_input.returnPressed.connect(self._emit_download)
        row.addWidget(self.url_input, 1)

        self.paste_button = QPushButton("Pegar")
        self.paste_button.setObjectName("Ghost")
        self.paste_button.setMinimumHeight(44)
        self.paste_button.clicked.connect(self._paste)
        row.addWidget(self.paste_button)

        self.download_button = QPushButton("Descargar")
        self.download_button.setObjectName("Primary")
        self.download_button.setMinimumHeight(44)
        self.download_button.clicked.connect(self._emit_download)
        row.addWidget(self.download_button)
        layout.addLayout(row)
        layout.addStretch(1)

        self._timer = QTimer(self)
        self._timer.setInterval(60)
        self._timer.timeout.connect(self._tick)

    def set_accent(self, primary: QColor, secondary: QColor) -> None:
        self._accent = primary
        self._accent_secondary = secondary
        self.update()

    def showEvent(self, event) -> None:
        self._timer.start()
        super().showEvent(event)

    def hideEvent(self, event) -> None:
        self._timer.stop()
        super().hideEvent(event)

    def set_busy(self, busy: bool) -> None:
        self.download_button.setDisabled(busy)
        self.download_button.setText("Enviando…" if busy else "Descargar")

    def clear_url(self) -> None:
        self.url_input.clear()

    def _tick(self) -> None:
        self._phase = (self._phase + 0.025) % (math.pi * 2)
        self.update()

    def _emit_download(self) -> None:
        url = self.url_input.text().strip()
        if url:
            self.download_requested.emit(url)

    def _paste(self) -> None:
        from PySide6.QtWidgets import QApplication

        text = QApplication.clipboard().text().strip()
        if text:
            self.url_input.setText(text)
            self.url_input.setFocus()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 26, 26)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, QColor("#14213a"))
        gradient.setColorAt(0.55, QColor("#0d1728"))
        gradient.setColorAt(1.0, QColor("#0a111d"))
        painter.fillPath(path, gradient)

        painter.save()
        painter.setClipPath(path)
        grid_pen = QColor(255, 255, 255, 7)
        painter.setPen(grid_pen)
        spacing = 42
        x = rect.left()
        while x < rect.right():
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += spacing
        y = rect.top()
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += spacing

        glow = QRadialGradient(
            rect.right() - 100,
            rect.top() + 30,
            270,
        )
        accent = QColor(self._accent)
        accent.setAlpha(52)
        glow.setColorAt(0.0, accent)
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(rect, glow)

        glow2 = QRadialGradient(
            rect.left() + 80,
            rect.bottom() + 20,
            240,
        )
        secondary = QColor(self._accent_secondary)
        secondary.setAlpha(32)
        glow2.setColorAt(0.0, secondary)
        glow2.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(rect, glow2)

        if not self._logo.isNull():
            painter.setOpacity(0.10)
            logo = self._logo.scaled(
                220,
                220,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            painter.drawPixmap(
                int(rect.right() - logo.width() - 24),
                int(rect.bottom() - logo.height() + 40),
                logo,
            )
        painter.restore()

        painter.setPen(QColor(255, 255, 255, 22))
        painter.drawPath(path)
        painter.setPen(QColor(255, 255, 255, 18))
        painter.drawLine(
            int(rect.left() + 26),
            int(rect.top() + 1),
            int(rect.right() - 26),
            int(rect.top() + 1),
        )


class LogConsole(QPlainTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Console")
        self.setReadOnly(True)
        self.setMaximumBlockCount(700)
        self.setMinimumHeight(150)
        self.setWordWrapMode(self.wordWrapMode())

    def append_line(self, message: str) -> None:
        cleaned = message.replace("\r", "").strip()
        if not cleaned:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        cursor = QTextCursor(self.document())
        cursor.movePosition(QTextCursor.End)
        formatter = QTextCharFormat()
        lowered = cleaned.lower()
        if "error" in lowered or "fallo" in lowered or "failed" in lowered:
            formatter.setForeground(QColor("#fda4af"))
        elif "ok" in lowered or "complet" in lowered or "success" in lowered:
            formatter.setForeground(QColor("#6ee7b7"))
        elif "warn" in lowered or "aviso" in lowered:
            formatter.setForeground(QColor("#fcd34d"))
        else:
            formatter.setForeground(QColor("#a8c0dd"))
        cursor.insertText(f"{timestamp}  {cleaned}\n", formatter)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()


class Toast(QFrame):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("Toast")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._label = QLabel("")
        self._label.setWordWrap(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.addWidget(self._label)
        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._animation = QPropertyAnimation(self._opacity, b"opacity", self)
        self._animation.setDuration(180)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._fade_out)
        self.hide()

    def show_message(
        self,
        message: str,
        tone: str = "info",
        duration: int = 3600,
    ) -> None:
        colors = {
            "success": ("rgba(52, 211, 153, 0.14)", "#9ff0c8"),
            "danger": ("rgba(244, 63, 94, 0.14)", "#fda4af"),
            "warning": ("rgba(251, 191, 36, 0.14)", "#f8d67d"),
            "info": ("rgba(56, 189, 248, 0.14)", "#9adcf8"),
        }
        background, foreground = colors.get(tone, colors["info"])
        self.setStyleSheet(
            f"QFrame#Toast {{ background: {background}; border: none; "
            f"border-radius: 12px; }} "
            f"QLabel {{ color: {foreground}; font-weight: 600; }}"
        )
        self._label.setText(message)
        self.adjustSize()
        self._reposition()
        self.show()
        self.raise_()
        self._animation.stop()
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.start()
        self._timer.start(duration)

    def _fade_out(self) -> None:
        self._animation.stop()
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.finished.connect(self._hide_after_fade)
        self._animation.start()

    def _hide_after_fade(self) -> None:
        self.hide()
        try:
            self._animation.finished.disconnect(self._hide_after_fade)
        except (RuntimeError, TypeError):
            pass

    def _reposition(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            return
        margin = 24
        self.move(
            max(margin, parent.width() - self.width() - margin),
            max(margin, parent.height() - self.height() - margin),
        )


class AnimatedStack(QStackedWidget):
    def set_current(self, index: int) -> None:
        if index == self.currentIndex():
            return
        page = self.widget(index)
        if page is None:
            return
        effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", page)
        animation.setDuration(170)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        self.setCurrentIndex(index)
        animation.finished.connect(lambda: page.setGraphicsEffect(None))
        animation.start(QPropertyAnimation.DeleteWhenStopped)


class EmptyState(QWidget):
    def __init__(self, title: str, subtitle: str) -> None:
        super().__init__()
        self.setAutoFillBackground(False)
        self.setMinimumHeight(130)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(6)
        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")
        title_label.setAlignment(Qt.AlignCenter)
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("Muted")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
