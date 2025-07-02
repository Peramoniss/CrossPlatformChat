#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtGui import QIcon
from client.views import ChatScreen
from client.views import HomeScreen
from shared.global_services.singleton_socket_service import Socket
from shared.global_utils.font_manager import FontManager



#|///////////////////////////////////////////////////////////////////////////|#
#| MAIN WINDOW                                                               |#
#|///////////////////////////////////////////////////////////////////////////|#

class MainWindow(QMainWindow):
    """
    Main window class.
    """

    def __init__(self):
        """
        Starts the main window for the application.
        """

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
        """
        Closes the connection with the server whenever the window is closed.
        """

        if Socket.is_initialized():
            try:
                self.chat_screen.send_message(text='\\q')
                socket = Socket.get_instance()
                socket.recv(1024)
                self.chat_screen.close_connection(socket)
            except Exception:
                pass

        event.accept()

    #|///////////////////////////////////////////////////////////////////////|#

    def create_chat_screen(self):
        """
        Creates the chat screen
        """

        if self.chat_screen:
            self.stacked_widget.removeWidget(self.chat_screen)
            self.chat_screen.deleteLater()

        self.chat_screen = ChatScreen(self.stacked_widget)
        self.chat_screen.closed.connect(self.handle_chat_closed)
        self.stacked_widget.addWidget(self.chat_screen)

    #|///////////////////////////////////////////////////////////////////////|#

    def handle_chat_closed(self):
        """
        Closes the connection to the chat.
        """
        # self.create_chat_screen()
        self.stacked_widget.setCurrentIndex(0)





def resource_path(relative_path):
    """
    Get the absolute path to a resource, works for dev and for PyInstaller bundles.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Not bundled, use current script directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#|///////////////////////////////////////////////////////////////////////////|#
#| MAIN FUNCTION                                                             |#
#|///////////////////////////////////////////////////////////////////////////|#

if __name__ == "__main__":
    """
    Starts the application for the client.
    """
    app = QApplication(sys.argv)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, ".."))
    # icon_path = os.path.join(root_dir, "shared", "global_assets", "icons", "app_icon.png")
    icon_path = resource_path("shared/global_assets/icons/app_icon.png")
    app.setWindowIcon(QIcon(icon_path))

    FontManager.load_fonts()    
    app.setFont(FontManager.PoppinsSemiBold)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
