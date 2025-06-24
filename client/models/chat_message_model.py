#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

from PyQt5.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QLabel,
    QHBoxLayout,
    QGraphicsDropShadowEffect
)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextDocument
from shared.global_utils.font_manager import FontManager



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class ChatMessageModel(QWidget):
    """
    Widget that represents a message in the chat screen.
    """
    def __init__(self, username, text, timestamp, client_message, parent=None):
        """
        Creates a new message in the chat screen.

        :param username: The name of the user that sent this message.
        :param text: The text of the message.
        :param timestamp: The datetime of the moment the message was sent.
        :param client_message: A boolean field that is True when the message was sent by the user and False when received by another user.
        :param parent: The parent widget of the message.
        """
        super().__init__(parent)

        self.client_message = client_message

        # Layout externo para alinhar
        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(10, 4, 10, 4)
        outer_layout.setSpacing(0)

        # Widget de espaço (1/3)
        spacer = QWidget()
        spacer.setFixedWidth(0)  # Será ajustado no resize

        # Container da mensagem
        self.message_container = QWidget()
        self.message_container.setObjectName("message_container")

        # Layout interno (conteúdo da mensagem)
        inner_layout = QVBoxLayout(self.message_container)
        inner_layout.setContentsMargins(10, 6, 10, 6)
        inner_layout.setSpacing(4)

        # Estilo do "balão"
        bg_color = "#d1eaff" if client_message else "#ffffff"
        border_color = "rgba(51, 122, 243, 40)" if client_message else "rgba(0, 0, 0, 20)"
        self.message_container.setStyleSheet(f"""
            QWidget#message_container {{
                border: 1px solid {border_color};                             
                background-color: {bg_color};
                border-radius: 8px;
                padding: 8px;
            }}
            QLabel {{
                background: transparent;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10) 
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 10))

        self.message_container.setGraphicsEffect(shadow)

        # Header: nome, hora, status
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)

        username_label = QLabel(username)
        username_label.setFont(FontManager.PoppinsSemiBold)
        username_label.setStyleSheet("font-size: 13px; color: #076dc5;" if client_message else "font-size: 13px; color: #333;")

        if client_message:
            status_and_time_label = QLabel(f"Sending... - {timestamp}")
            status_and_time_label.setFont(FontManager.PoppinsMedium)
            status_and_time_label.setStyleSheet("font-size: 12px; color: #888;")
            header_layout.addWidget(username_label)
            header_layout.addStretch()
            header_layout.addWidget(status_and_time_label)
            self.status_label = status_and_time_label
        else:
            timestamp_label = QLabel(timestamp)
            timestamp_label.setFont(FontManager.PoppinsMedium)
            timestamp_label.setStyleSheet("font-size: 12px; color: #999;")
            header_layout.addWidget(timestamp_label)
            header_layout.addStretch()
            header_layout.addWidget(username_label)

        # Mensagem
        message_label = QLabel(text)
        message_label.setTextFormat(Qt.RichText)
        message_label.setFont(FontManager.PoppinsRegular)
        message_label.setStyleSheet("font-size: 14px; color: #000; background: transparent;")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignLeft if client_message else Qt.AlignRight)

        inner_layout.addLayout(header_layout)
        inner_layout.addWidget(message_label)

        # Monta layout externo
        if client_message:
            outer_layout.addWidget(self.message_container, 2)
            outer_layout.addStretch(1)
        else:
            outer_layout.addStretch(1)
            outer_layout.addWidget(self.message_container, 2)

        self.setLayout(outer_layout)

    def resizeEvent(self, event):
        if self.parent():
            total_width = self.parent().width()
            max_width = int(total_width * 2 / 3)
            self.message_container.setMaximumWidth(max_width)
        super().resizeEvent(event)
