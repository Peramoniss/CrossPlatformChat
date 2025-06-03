#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from shared.singleton_socket import Socket
from views import ChatScreen
from views import HomeScreen
from utils.font_manager import FontManager



#|///////////////////////////////////////////////////////////////////////////|#
#| MAIN WINDOW                                                               |#
#|///////////////////////////////////////////////////////////////////////////|#

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlaBlaBla Chat")
        self.resize(900, 500)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.first_screen = HomeScreen(self.stacked_widget, self)
        self.chat_screen = ChatScreen(self.stacked_widget)

        self.stacked_widget.addWidget(self.first_screen)
        self.stacked_widget.addWidget(self.chat_screen)
    
    def closeEvent(self, event):
        if Socket.is_initialized():
            try:
                socket_instance = Socket.get_instance()
                socket_instance.soquete.send('\q'.encode())
                self.chat_screen.close_connection(socket_instance.soquete)
            except:
                pass

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
