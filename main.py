#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import sys

from PyQt5.QtWidgets import (
    QApplication, 
    QWidget, 
    QPushButton, 
    QVBoxLayout, 
    QHBoxLayout,
    QTextEdit, 
    QLineEdit, 
    QLabel, 
    QScrollArea, 
    QMainWindow, 
    QStackedWidget,
    QFrame
)

from globals.singletonSocket import Socket
from screens import ChatScreen
from screens import HomeScreen
from utils.font_manager import FontManager



#|///////////////////////////////////////////////////////////////////////////|#
#| MAIN WINDOW                                                               |#
#|///////////////////////////////////////////////////////////////////////////|#

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlaBlaBla Chat")
        self.resize(900, 500)

        # self.soquete = None

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.first_screen = HomeScreen(self.stacked_widget, self)
        self.chat_screen = ChatScreen(self.stacked_widget)

        self.stacked_widget.addWidget(self.first_screen)
        self.stacked_widget.addWidget(self.chat_screen)
    
    def closeEvent(self, event):
        print("Janela foi fechada!")
        # Aqui você pode desconectar sockets, parar threads, salvar estado, etc.
        Socket.get_instance().soquete.send('\q'.encode())
        self.chat_screen.close_connection(Socket.get_instance().soquete)

        # Se quiser permitir o fechamento:
        event.accept()



#|///////////////////////////////////////////////////////////////////////////|#
#| MAIN FUNCTION                                                             |#
#|///////////////////////////////////////////////////////////////////////////|#

if __name__ == "__main__":
    app = QApplication(sys.argv)
    FontManager.load_fonts()    
    app.setFont(FontManager.PoppinsSemiBold)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
