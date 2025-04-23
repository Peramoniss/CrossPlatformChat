#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

from PyQt5.QtWidgets import (
    QWidget, 
    QPushButton, 
    QVBoxLayout
)

from PyQt5.QtCore import (
    Qt
)

import socket as s
from globals import singletonSocket
from screens.chat_screen import ChatScreen

#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS                                                                     |#
#|///////////////////////////////////////////////////////////////////////////|#

def close_connection(soquete):
    print("Closing the connection")
    soquete.close()

def start_client():
    global username
    soquete = s.socket(s.AF_INET, s.SOCK_STREAM)

    # ip = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    # porta = int(sys.argv[2]) if len(sys.argv) > 2 else 65432
    ip = 'localhost'
    porta = 65432

    # username = input("Select an username: ")
    username = 'TESTE'
    server_address = (ip, porta)
    print(f"Connecting to {server_address}")
    soquete.connect(server_address)

    try:
        data = soquete.recv(1024)
        print(f"Received: {data.decode()}")
        return soquete
    except:
        close_connection(soquete)

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

    def go_to_chat(self):
        soquete = start_client()
        singletonSocket.Socket(soquete)
        self.main_window.chat_screen.start_connection()
        self.main_window.stacked_widget.setCurrentIndex(1)
