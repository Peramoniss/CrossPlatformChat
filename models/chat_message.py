#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

from PyQt5.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QLabel,
    QHBoxLayout
)

from PyQt5.QtCore import Qt
from utils.font_manager import FontManager



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class ChatMessage(QWidget):
    def __init__(self, username, text, timestamp, client_message):
        super().__init__()

        self.client_message = client_message

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)
        self.setLayout(layout)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)

        if client_message:
            sender_html = f"<b><span style='color: green;'>{username}</span></b>"
        else:
            sender_html = f"<b><span style='color: #333;'>{username}</b>"
        user_label = QLabel(sender_html)
        user_label.setFont(FontManager.PoppinsSemiBold)
        user_label.setStyleSheet("font-size: 13px;")
        user_label.setAlignment(Qt.AlignLeft)

        time_label = QLabel(timestamp)
        time_label.setFont(FontManager.PoppinsMedium)
        time_label.setStyleSheet("color: #999; font-size: 12px;")
        time_label.setAlignment(Qt.AlignRight)
        
        header_layout.addWidget(user_label)
        header_layout.addStretch()
        header_layout.addWidget(time_label)

        message_label = QLabel(text)
        message_label.setFont(FontManager.PoppinsRegular)
        message_label.setStyleSheet("color: #000; font-size: 14px;")
        message_label.setWordWrap(True)
        message_label.setContentsMargins(0, 0, 0, 0)

        if client_message:
            self.status_label = QLabel("Enviando...")  # ou "", se preferir vazio
            self.status_label.setStyleSheet("font-size: 10px; color: #888888;")
            self.status_label.setVisible(True)
            layout.addWidget(self.status_label)

        layout.addLayout(header_layout)
        layout.addWidget(message_label)
