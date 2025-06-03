#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from shared.singleton_socket import Socket
from views.chat_screen import ChatScreen
from utils.connection_manager import *



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class HomeScreen(QWidget):
    def __init__(self, stacked_widget, main_window):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.main_window = main_window
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        button = QPushButton("Ir para o chat")
        button.clicked.connect(self.go_to_chat)

        layout.addWidget(button)
        self.setLayout(layout)
    
    #|///////////////////////////////////////////////////////////////////////|#

    def go_to_chat(self):
        network_socket = start_client()
        Socket(network_socket)
        self.main_window.chat_screen.start_connection()
        self.main_window.stacked_widget.setCurrentIndex(1)
