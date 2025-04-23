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
#| CLASS                                                                     |#
#|///////////////////////////////////////////////////////////////////////////|#

class ChatMessage(QWidget):
    def __init__(self, username, text, timestamp):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)
        self.setLayout(layout)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)

        user_label = QLabel(username)
        user_label.setFont(FontManager.PoppinsSemiBold)
        user_label.setStyleSheet("color: #333; font-size: 13px;")
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

        layout.addLayout(header_layout)
        layout.addWidget(message_label)
