from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPen,
    QPixmap,
    QRadialGradient,
    QTextCharFormat,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
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


def add_shadow(widget: QWidget, *, blur: int = 40, y: int = 18) -> None:
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, y)
    shadow.setColor(QColor(17, 17, 22, 22))
    widget.setGraphicsEffect(shadow)


class Card(QFrame):
    def __init__(self, parent: QWidget | None = None, *, subtle: bool = False) -> None:
        super().__init__(parent)
        self.setObjectName("SubtleCard" if subtle else "Card")
        self._content = QVBoxLayout(self)
        self._content.setContentsMargins(24, 24, 24, 24)
        self._content.setSpacing(14)
        if not subtle:
            add_shadow(self)

    @property
    def content(self) -> QVBoxLayout:
        return self._content


class FeatureCard(Card):
    def __init__(
        self,
        number: str,
        title: str,
        body: str,
        accent: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setMinimumHeight(174)
        badge = QLabel(number)
        badge.setStyleSheet(
            f"color: {accent}; font-size: 12px; font-weight: 800; "
            f"letter-spacing: 1px;"
        )
        self.content.addWidget(badge)
        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")
        self.content.addWidget(title_label)
        body_label = QLabel(body)
        body_label.setObjectName("Muted")
        body_label.setWordWrap(True)
        self.content.addWidget(body_label)
        self.content.addStretch(1)


class StatCard(Card):
    def __init__(
        self,
        caption: str,
        value: str = "—",
        accent: str = "#6d5ef7",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setMinimumHeight(122)
        top = QHBoxLayout()
        top.setSpacing(8)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {accent}; border-radius: 4px;")
        top.addWidget(dot)
        caption_label = QLabel(caption.upper())
        caption_label.setObjectName("StatCaption")
        top.addWidget(caption_label)
        top.addStretch(1)
        self.content.addLayout(top)
        self._value = QLabel(value)
        self._value.setObjectName("StatValue")
        self.content.addWidget(self._value)
        self._detail = QLabel("")
        self._detail.setObjectName("Muted")
        self.content.addWidget(self._detail)

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


class NavButton(QPushButton):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setObjectName("NavButton")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(36)


class GradientLabel(QLabel):
    def __init__(
        self,
        text: str,
        colors: tuple[str, str] = ("#6d5ef7", "#ff7a59"),
    ) -> None:
        super().__init__(text)
        self._colors = colors
        self.setAlignment(Qt.AlignCenter)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(
            "font-size: 52px; font-weight: 800; letter-spacing: -2px;"
        )

    def set_colors(self, colors: tuple[str, str]) -> None:
        self._colors = colors
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setFont(self.font())
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(self._colors[0]))
        gradient.setColorAt(1.0, QColor(self._colors[1]))
        painter.setPen(QPen(QBrush(gradient), 1))
        painter.drawText(
            self.contentsRect(),
            int(self.alignment()),
            self.text(),
        )


class HeroCard(QWidget):
    download_requested = Signal(str)

    def __init__(self, accent: QColor, accent_secondary: QColor) -> None:
        super().__init__()
        self.setObjectName("Hero")
        self.setMinimumHeight(420)
        self._accent = accent
        self._accent_secondary = accent_secondary
        self._logo = QPixmap(str(asset_path("logo.png")))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 44, 28, 34)
        layout.setSpacing(10)

        kicker = QLabel("GOOGLE DRIVE · SESIÓN AISLADA")
        kicker.setObjectName("HeroKicker")
        kicker.setAlignment(Qt.AlignCenter)
        layout.addWidget(kicker)

        first_line = QLabel("Tus archivos de Drive,")
        first_line.setObjectName("HeroTitle")
        first_line.setAlignment(Qt.AlignCenter)
        layout.addWidget(first_line)

        self.gradient = GradientLabel(
            "sin fricción.",
            (accent.name(), accent_secondary.name()),
        )
        layout.addWidget(self.gradient)

        subtitle = QLabel(
            "Una sesión aislada de Chrome, descargas resilientes y una interfaz "
            "que nunca se queda esperando."
        )
        subtitle.setObjectName("HeroText")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setMaximumWidth(620)
        subtitle.setMinimumHeight(78)
        subtitle.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout.addWidget(subtitle, 0, Qt.AlignHCenter)
        layout.addSpacing(14)

        search = QFrame()
        search.setObjectName("SearchCard")
        search.setMaximumWidth(760)
        search_layout = QHBoxLayout(search)
        search_layout.setContentsMargins(8, 8, 8, 8)
        search_layout.setSpacing(8)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Pega un enlace de Google Drive para comenzar"
        )
        self.url_input.setMinimumHeight(46)
        self.url_input.returnPressed.connect(self._emit_download)
        search_layout.addWidget(self.url_input, 1)

        self.paste_button = QPushButton("Pegar")
        self.paste_button.setObjectName("Ghost")
        self.paste_button.setMinimumHeight(46)
        self.paste_button.clicked.connect(self._paste)
        search_layout.addWidget(self.paste_button)

        self.download_button = QPushButton("Descargar")
        self.download_button.setObjectName("Primary")
        self.download_button.setMinimumHeight(46)
        self.download_button.clicked.connect(self._emit_download)
        search_layout.addWidget(self.download_button)
        add_shadow(search, blur=28, y=12)
        layout.addWidget(search, 0, Qt.AlignHCenter)

        trust = QHBoxLayout()
        trust.setSpacing(18)
        trust.addStretch(1)
        for text in (
            "Perfil de Chrome aislado",
            "Reintentos automáticos",
            "Todo se queda en local",
        ):
            label = QLabel(text)
            label.setObjectName("Tiny")
            trust.addWidget(label)
        trust.addStretch(1)
        layout.addLayout(trust)
        layout.addStretch(1)

    def set_accent(self, primary: QColor, secondary: QColor) -> None:
        self._accent = primary
        self._accent_secondary = secondary
        self.gradient.set_colors((primary.name(), secondary.name()))
        self.update()

    def set_busy(self, busy: bool) -> None:
        self.download_button.setDisabled(busy)
        self.download_button.setText("Enviando…" if busy else "Descargar")

    def clear_url(self) -> None:
        self.url_input.clear()

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
        painter.fillRect(self.rect(), Qt.transparent)

        painter.setPen(QColor(17, 17, 22, 12))
        spacing = 28
        for x in range(0, self.width(), spacing):
            for y in range(0, self.height(), spacing):
                painter.drawPoint(x, y)

        glow = QRadialGradient(self.width() * 0.16, 40, self.width() * 0.42)
        primary = QColor(self._accent)
        primary.setAlpha(42)
        glow.setColorAt(0.0, primary)
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), glow)

        glow2 = QRadialGradient(self.width() * 0.86, 20, self.width() * 0.38)
        secondary = QColor(self._accent_secondary)
        secondary.setAlpha(36)
        glow2.setColorAt(0.0, secondary)
        glow2.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), glow2)

        if not self._logo.isNull():
            painter.setOpacity(0.055)
            logo = self._logo.scaled(
                250,
                250,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            painter.drawPixmap(
                int(self.width() - logo.width() - 30),
                int(self.height() - logo.height() + 34),
                logo,
            )


class LogConsole(QPlainTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Console")
        self.setReadOnly(True)
        self.setMaximumBlockCount(700)
        self.setMinimumHeight(180)

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
            formatter.setForeground(QColor("#d8d3c8"))
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
            "success": "#6ee7b7",
            "danger": "#fda4af",
            "warning": "#fcd34d",
            "info": "#c7d2fe",
        }
        foreground = colors.get(tone, colors["info"])
        self.setStyleSheet(
            "QFrame#Toast { background: #111114; border: none; "
            "border-radius: 14px; } "
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
