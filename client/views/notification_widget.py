from PyQt5.QtCore import pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QGraphicsOpacityEffect, QVBoxLayout


class NotificationWidget(QWidget):
    closed = pyqtSignal()

    def __init__(self, message, duration, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Layout com margem interna
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget(self)
        container.setObjectName("container")
        container.setStyleSheet("""
            QWidget#container {
                background-color: rgba(50, 50, 50, 200);
                border-radius: 8px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)

        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(12, 10, 12, 10)
        container_layout.setSpacing(8)

        self.label = QLabel(message)
        self.label.setWordWrap(True)
        container_layout.addWidget(self.label)

        container_layout.addStretch()

        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #ccc;
            }
        """)
        close_btn.clicked.connect(self._close)
        container_layout.addWidget(close_btn)

        main_layout.addWidget(container)

        # Fade effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade.setDuration(300)
        self.fade.setStartValue(0)
        self.fade.setEndValue(1)
        self.fade.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade.finished.connect(self._on_fade_in_complete)

        self.fade.start()

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._start_fade_out)
        self.timer.start(duration)

    def _on_fade_in_complete(self):
        pass  # No-op

    def _start_fade_out(self):
        self.fade = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade.setDuration(300)
        self.fade.setStartValue(1)
        self.fade.setEndValue(0)
        self.fade.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade.finished.connect(self._close)
        self.fade.start()

    def _close(self):
        self.close()
        self.closed.emit()
