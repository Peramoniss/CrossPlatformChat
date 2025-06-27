#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import os
from client.services.notification_service import NotificationManager
import shared.global_services.encryption_service as encryption
from shared.global_services.singleton_socket_service import Socket as singleton_socket
from shared.global_utils.font_manager import FontManager
from shared.global_services.connection_manager import start_client
import struct
from PyQt5.QtSvg import QSvgRenderer

from PyQt5.QtGui import (
    QPainter, 
    QPainterPath, 
    QLinearGradient, 
    QColor, 
    QFontMetrics, 
    QImage,
    QPixmap, 
    QBrush
)

from PyQt5.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QLabel, 
    QLineEdit, 
    QPushButton,
    QSpacerItem, 
    QSizePolicy, 
    QProgressBar, 
    QGraphicsDropShadowEffect
)

from PyQt5.QtCore import (
    Qt, 
    QThread, 
    pyqtSignal
)



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class ConnectionThread(QThread):
    """
    Class for a different thread to handle the connection to the server while the graphics run in another thread.
    """
    connected = pyqtSignal(object)
    error = pyqtSignal(Exception)

    def __init__(self, room_code):
        """
        Creates the thread to connect to a room.

        :param room_code: The alphanumeric code to the server.
        """
        super().__init__()
        self._is_running = True
        self.room_code = room_code

    def run(self):
        """
        Runs the server connection thread, formalizing the safe channel.
        """
        try:
            if not self._is_running:
                return
            
            self.network_socket = start_client(self.room_code)

            private_key, public_pem = encryption.create_rsa_keys()
            singleton_socket.initialize(self.network_socket)
            socket = singleton_socket.get_instance()

            socket.send(public_pem)

            encrypted_aes = self.network_socket.recv(1024)
            aes_key = encryption.rsa_decrypt(private_key, encrypted_aes)
            singleton_socket.set_key(aes_key)

            self.connected.emit(self.network_socket)
        except Exception as e:
            self.error.emit(e)


    def stop(self):
        """
        Whenever an error occur, stop running the thread.
        """
        self._is_running = False
        if self.network_socket:
            try:
                self.network_socket.close()
            except:
                pass

#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class GradientLabel(QLabel):
    """
    Class for the chat title label stylized with gradient colors. 
    """

    def __init__(self, text="", parent=None):
        """
        Initialize the chat title label stylized with gradient colors.

        :param text: The label's text.
        :param parent: Parent widget. Default is None.
        """
        super().__init__(text, parent)
        self.gradient_colors = [(0, QColor(18, 62, 205)), (1, QColor(40, 115, 246))]

    def paintEvent(self, event):
        """
        Paints the label.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        rect = self.rect()
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())

        for pos, color in self.gradient_colors:
            gradient.setColorAt(pos, color)

        font = self.font()
        text = self.text()
        painter.setFont(font)
        metrics = QFontMetrics(font)
        text_rect = metrics.boundingRect(text)
        x = 0
        y = (rect.height() + text_rect.height()) / 2 - metrics.descent()
        path = QPainterPath()
        path.addText(x, y, font, text)
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class HomeScreen(QWidget):
    """
    Class for the home screen.
    """
    def __init__(self, stacked_widget, main_window):
        """
        Creates the home screen for the chat application.

        :param stacked_widget: Parent widget.
        :param mains_window: Main window widget. Used to keep track of close and other methods.
        """

        super().__init__()
        self.stacked_widget = stacked_widget
        self.main_window = main_window
        self.thread = None

        # Main vertical layour with padding in the corners
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)
        self.setLayout(self.main_layout)
        self.setFont(FontManager.PoppinsSemiBold)

        # "Bla Bla Bla" and "Chat" labels
        self.top_widget = QWidget()
        self.top_layout = QVBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        self.top_widget.setLayout(self.top_layout)

        self.top_layout.addStretch()

        # New container for both labels satcked vertically
        text_column = QWidget()
        text_column_layout = QVBoxLayout()
        text_column_layout.setContentsMargins(0, 0, 0, 0)
        text_column_layout.setSpacing(0)  # small, positive padding
        text_column.setLayout(text_column_layout)

        line1 = GradientLabel("Bla Bla Bla Chat")
        line1.setStyleSheet("font-size: 68px; font-weight: bold; color: black;")
        line1.setFont(FontManager.PoppinsSemiBold)
        line1.setFixedHeight(64)

        line2 = GradientLabel("Powered by the Bla Bla Bla Protocol")
        line2.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        line2.setFont(FontManager.PoppinsSemiBold)
        line2.setFixedHeight(22)

        text_column_layout.addWidget(line1, alignment=Qt.AlignCenter)
        text_column_layout.addWidget(line2, alignment=Qt.AlignCenter)

        self.top_layout.addWidget(text_column, alignment=Qt.AlignCenter)

        self.top_layout.addStretch()

        # White container for the bottom 2/3
        self.right_widget = QWidget()
        self.right_widget.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 40))

        self.right_widget.setGraphicsEffect(shadow)

        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(20, 20, 20, 20)
        self.right_layout.setSpacing(15)
        self.right_widget.setLayout(self.right_layout)

        # Room code field
        self.room_code_input = QLineEdit()
        self.room_code_input.setPlaceholderText("Enter room code")
        self.room_code_input.setFixedHeight(40)
        self.room_code_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding-left: 10px;
                font-size: 14px;
            }
        """)
        self.right_layout.addWidget(self.room_code_input)

        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding-left: 10px;
                font-size: 14px;
            }
        """)
        self.right_layout.addWidget(self.username_input)

        # Enter button
        self.button = QPushButton("Enter")
        self.button.setFixedHeight(40)
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
        self.right_layout.addWidget(self.button)

        # Cancel button (DEPRECATED)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #E24A4A;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #B43535;
            }
        """)
        self.cancel_button.hide()
        self.cancel_button.clicked.connect(self.cancel_connection)
        self.right_layout.addWidget(self.cancel_button)

        # Progress bar for when connecting
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: #e6f0fa;
                padding: 1px;
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #6aacf9,
                    stop: 1 #357ABD
                );
            }
        """)
        self.right_layout.addWidget(self.progress_bar)

        self.version_label = QLabel("Version 1.0.0 – Background image by Steve Schoger (CC BY 4.0)")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setStyleSheet("font-size: 12px; color: #888888;")

        self.right_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.right_layout.addWidget(self.version_label, alignment=Qt.AlignCenter)
        
        self.main_layout.addWidget(self.top_widget, 1)
        self.main_layout.addWidget(self.right_widget, 2)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(base_dir, ".."))
        root_dir = os.path.abspath(os.path.join(root_dir, ".."))
        icon_path = os.path.join(root_dir, "shared", "global_assets", "icons", "morphing-diamonds.svg")
        
        self.background_brush = self.create_tiled_svg_brush(icon_path)
        self.notification_manager = NotificationManager(self)
        self.update()

    #|///////////////////////////////////////////////////////////////////////|#

    def go_to_chat(self):
        """
        Changes the screen for the chat screen whenever the connection is established.
        """

        room_code = self.room_code_input.text()
        if not room_code:
            self.notification_manager.show_notification("Room code is required.")
            return
        
        username = self.username_input.text().strip()

        if not username:
            self.notification_manager.show_notification("Username is required.")
            return

        self.button.setEnabled(False)
        self.username_input.setEnabled(False)
        self.room_code_input.setEnabled(False)
        self.progress_bar.show()
        self.cancel_button.show()

        self.thread = ConnectionThread(room_code)
        self.thread.connected.connect(self.on_connected)
        self.thread.error.connect(self.on_connection_error)
        self.thread.start()
    
    #|///////////////////////////////////////////////////////////////////////|#

    def cancel_connection(self):
        """
        Tries to cancel the connection. Deprecated since it shuts the server down.
        """
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()

        self.progress_bar.hide()
        self.cancel_button.hide()
        self.button.setEnabled(True)
        self.username_input.setEnabled(True)
        self.room_code_input.setEnabled(True)
    
    #|///////////////////////////////////////////////////////////////////////|#

    def on_connected(self):
        """
        Handles the view when the connection is established.
        """
        self.progress_bar.hide()
        self.cancel_button.hide()
        self.button.setEnabled(True)
        self.username_input.setEnabled(True)
        self.room_code_input.setEnabled(True)

        
        self.main_window.chat_screen.start_connection(self.username_input.text().strip())
        self.main_window.stacked_widget.setCurrentIndex(1)
    
    #|///////////////////////////////////////////////////////////////////////|#

    def on_connection_error(self, exception):
        """
        Handles an error encountered when trying to connect.

        :param exception: The exception or error to be showed.
        """
        self.progress_bar.hide()
        self.cancel_button.hide()
        self.button.setEnabled(True)
        self.username_input.setEnabled(True)
        self.room_code_input.setEnabled(True)
        self.notification_manager.show_notification(f"Connection error: {str(exception)}")
    #|///////////////////////////////////////////////////////////////////////|#
    
    def create_tiled_svg_brush(self, svg_path):
        """
        Creates the brush to paint the label.

        :param svg_path: The path to the svg icon file. 
        """
        renderer = QSvgRenderer(svg_path)
        image = QImage(60, 60, QImage.Format_ARGB32)
        image.fill(Qt.transparent)

        painter = QPainter(image)
        renderer.render(painter)
        painter.end()

        pixmap = QPixmap.fromImage(image)
        return QBrush(pixmap)

    #|///////////////////////////////////////////////////////////////////////|#

    def paintEvent(self, event):
        """
        Handles the paint event.

        :param event: The paint event.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fundo colorido
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        if self.background_brush:
            painter.setOpacity(0.05)
            painter.fillRect(self.rect(), self.background_brush)
            painter.setOpacity(1.0)

        super().paintEvent(event)
