#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QProgressBar, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from shared.singleton_socket import Socket
from client.views.chat_screen import ChatScreen
from shared.global_utils.connection_manager import start_client
from PyQt5.QtGui import QMovie



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class ConnectionThread(QThread):
    connected = pyqtSignal(object)

    def run(self):
        network_socket = start_client()
        self.connected.emit(network_socket)



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

"""
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
"""


class HomeScreen(QWidget):
    def __init__(self, stacked_widget, main_window):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.main_window = main_window

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setSpacing(20)
        self.setLayout(self.layout)

        # Campo de nome de usuário
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedSize(250, 40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding-left: 10px;
                font-size: 14px;
            }
        """)
        self.layout.addWidget(self.username_input, alignment=Qt.AlignCenter)

        # Botão de entrada
        self.button = QPushButton("Enter")
        self.button.setFixedSize(250, 40)
        self.button.clicked.connect(self.go_to_chat)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:disabled {
                background-color: #999;
            }
        """)
        self.layout.addWidget(self.button, alignment=Qt.AlignCenter)

        # Mensagem de erro (oculta por padrão)
        self.error_label = QLabel("Username is required.")
        self.error_label.setStyleSheet("color: red; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        self.layout.addWidget(self.error_label)

        # Spacer para empurrar barra para baixo
        self.layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Barra de progresso na parte inferior
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                margin-left: 15px;
                margin-right: 15px;
                margin-bottom: 15px;
                border: 1px solid #ccc;
                border-radius: 10px;
                background-color: #f0f0f0;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4A90E2;
                border-radius: 10px;
            }
        """)
        self.layout.addWidget(self.progress_bar)

    #|///////////////////////////////////////////////////////////////////////|#

    def go_to_chat(self):
        username = self.username_input.text().strip()

        if not username:
            self.error_label.show()
            return

        self.error_label.hide()
        self.button.setEnabled(False)
        self.username_input.setEnabled(False)
        self.progress_bar.show()

        self.thread = ConnectionThread()
        self.thread.connected.connect(self.on_connected)
        self.thread.start()

    def on_connected(self, network_socket):
        self.progress_bar.hide()
        self.button.setEnabled(True)
        self.username_input.setEnabled(True)

        Socket(network_socket)
        self.main_window.chat_screen.start_connection(self.username_input.text().strip())
        self.main_window.stacked_widget.setCurrentIndex(1)
