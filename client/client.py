#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtGui import QIcon
from client.views import ChatScreen
from client.views import HomeScreen
from shared.global_services.singleton_socket import Socket
from shared.global_utils.font_manager import FontManager



#|///////////////////////////////////////////////////////////////////////////|#
#| MAIN WINDOW                                                               |#
#|///////////////////////////////////////////////////////////////////////////|#

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bla Bla Bla Chat")
        self.resize(900, 500)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.home_screen = HomeScreen(self.stacked_widget, self)
        self.stacked_widget.addWidget(self.home_screen)
        self.chat_screen = None
        self.create_chat_screen()
        self.chat_screen.closed.connect(self.handle_chat_closed)
    
    #|///////////////////////////////////////////////////////////////////////|#

    def closeEvent(self, event):
        if Socket.is_initialized():
            try:
                socket_instance = Socket.get_instance()
                socket_instance.soquete.send('\q'.encode())
                self.chat_screen.close_connection(socket_instance.soquete)
            except:
                pass

        event.accept()

    #|///////////////////////////////////////////////////////////////////////|#

    def create_chat_screen(self):
        if self.chat_screen:
            self.stacked_widget.removeWidget(self.chat_screen)
            self.chat_screen.deleteLater()

        self.chat_screen = ChatScreen(self.stacked_widget)
        self.chat_screen.closed.connect(self.handle_chat_closed)
        self.stacked_widget.addWidget(self.chat_screen)

    #|///////////////////////////////////////////////////////////////////////|#

    def handle_chat_closed(self):
        self.create_chat_screen()
        self.stacked_widget.setCurrentIndex(0)


#|///////////////////////////////////////////////////////////////////////////|#
#| MAIN FUNCTION                                                             |#
#|///////////////////////////////////////////////////////////////////////////|#

if __name__ == "__main__":
    app = QApplication(sys.argv)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, ".."))
    icon_path = os.path.join(root_dir, "shared", "global_assets", "icons", "app_icon.png")
    app.setWindowIcon(QIcon(icon_path))

    FontManager.load_fonts()    
    app.setFont(FontManager.PoppinsSemiBold)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
