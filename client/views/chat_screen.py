#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

from asyncio import sleep
import os
import json
import uuid
import threading
from client.models.chat_message_model import ChatMessageModel
from client.services.message_receiver_service import MessageReceiverService
import shared.global_services.encryption_service as encryption   
from shared.global_utils.font_manager import FontManager
from shared.global_services.singleton_socket_service import Socket as singletonSocket
from shared.global_definitions import MessageType 

from PyQt5.QtWidgets import (
    QWidget, 
    QPushButton, 
    QVBoxLayout, 
    QHBoxLayout,
    QTextEdit,
    QLabel, 
    QScrollArea,
    QSizePolicy,
    QFrame,
    QApplication
)

from PyQt5.QtCore import (
    Qt, 
    QDateTime,
    QTimer,
    QSize,
    pyqtSignal
)

from PyQt5.QtGui import (
    QIcon,
    QTextCharFormat,
    QFont
)

#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class ChatScreen(QWidget):
    """
    A class that defines the behavior and visuleave_request_signal = pyqtSignal()al components of the chat screen. 
    """

    #Signals for inter-thread evenleave_confirmation_signalts
    new_message_signal = pyqtSignal(object)  
    leave_request_signal = pyqtSignal()
    leave_confirmation_signal = pyqtSignal()
    closed = pyqtSignal()

    ###########################################################################

    def __init__(self, stacked_widget):
        """
        Initializes the screen class.

        :param stacked_widget: The widget (screen class) that will act as parent of this one.
        """
        super().__init__()
        self.stacked_widget = stacked_widget
        self.unread_messages = [] #List that controls the massages that the user haven't read yet
        self.running = False 

        self.new_message_signal.connect(self.handle_incoming_message) #Sets the function to execute in the event of receiving a new message
        self.leave_request_signal.connect(self.handle_leave_request)
        self.leave_confirmation_signal.connect(self.handle_leave_confirmation)
        self.setup_user_interface()

        app = QApplication.instance()
        if app:
            app.focusChanged.connect(self.on_focus_changed) #Sets the function to execute in the event of changing focus. Important to control the read messages.

    ###########################################################################

    def setup_user_interface(self):
        """
        Creates the basic screen elements for the chat screen.
        """
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setup_app_bar()
        self.setup_chat_area()
        self.setup_input_area()
        
    ###########################################################################

    def setup_app_bar(self):
        """
        Creates the app title bar on the screen.
        """
        app_bar_container = QFrame()
        app_bar_container.setStyleSheet("background: transparent;")

        app_bar_layout = QVBoxLayout(app_bar_container)
        app_bar_layout.setContentsMargins(0, 0, 0, 0)

        app_bar = QFrame()
        app_bar.setFixedHeight(50)
        app_bar.setStyleSheet("""
            QFrame {
                background-color: white;
                color: black;
                border-bottom: 1px solid rgba(0, 0, 0, 40);
                padding-bottom: 1px;
            }
        """)

        inner_layout = QHBoxLayout(app_bar)
        inner_layout.setContentsMargins(10, 0, 10, 0)
        inner_layout.setAlignment(Qt.AlignVCenter)

        back_button = QPushButton()
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        icon_path = os.path.join(BASE_DIR, "shared", "global_assets", "icons", "arrow-back.svg")
        back_button.setIcon(QIcon(icon_path))
        back_button.setIconSize(QSize(20, 20))
        back_button.setFixedSize(40, 40)
        back_button.setStyleSheet("""
            background-color: transparent;
            border: none;
        """)
        back_button.clicked.connect(self.handle_back_navigation)

        title_label = QLabel("Bla Bla Bla Chat")
        title_label.setContentsMargins(0, 4, 0, 0)
        title_label.setStyleSheet("""
            color: black;
            font-weight: bold;
            font-size: 17px;
            border: none;
            background: transparent;
        """)

        inner_layout.addWidget(back_button)
        inner_layout.addWidget(title_label)
        inner_layout.addStretch()

        app_bar_layout.addWidget(app_bar)
        self.main_layout.addWidget(app_bar_container)

    ###########################################################################

    def setup_chat_area(self):
        """
        Creates the messaging board for the chat messages on the screen.
        """
        self.chat_area = QVBoxLayout()
        self.chat_area.addStretch(1)

        container = QWidget()
        container.setLayout(self.chat_area)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(container)
        self.scroll.setStyleSheet("background-color: #F0F0F0; border: none;")

        self.main_layout.addWidget(self.scroll)

    #############################################################leave_request_signal##############

    def setup_input_area(self):
        """
        Creates the input text field on the screen.
        """
        #TODO: Implement bold, italic, and other text configurations
        input_layout = QHBoxLayout()

        self.input_field = SingleLineTextEdit()
        self.input_field.setFixedHeight(48)
        self.input_field.setFont(FontManager.PoppinsMedium)
        self.input_field.setStyleSheet(self.get_common_style())
        self.input_field.returnPressed.connect(self.send_message)

        send_button = QPushButton("Send")
        send_button.setFixedHeight(48)
        send_button.setFont(FontManager.PoppinsMedium)
        send_button.setStyleSheet(self.get_common_style())
        send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_button)

        input_frame = QFrame()
        input_frame.setLayout(input_layout)
        input_frame.setStyleSheet("""
            padding: 5px;
            background-color: white;
            border-top: 1px solid rgba(0, 0, 0, 40);
        """)

        self.scroll.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 4px 2px 4px 2px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background: rgba(100, 100, 100, 80);
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: rgba(100, 100, 100, 160);
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        self.main_layout.addWidget(input_frame)

    ###########################################################################

    def get_common_style(self):
        """
        :return: A css text with the basic screen style. 
        """
        return """
            QTextEdit, QPushButton {
                border: 1px solid #ccc;
                border-radius: 7px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }

            QTextEdit:focus, QPushButton:hover {
                border: 2px solid #0078d7;
                outline: none;
            }

            QPushButton {
                background-color: #0078d7;
                color: white;
            }

            QPushButton:hover {
                background-color: #005a9e;
            }

            QPushButton:pressed {
                background-color: #004578;
            }
        """

    ###########################################################################

    def start_connection(self, username):
        """
        Starts the connection with the second user. 
        Opens a new thread to deal with the communication with the server.
        Called when the screen is loaded.
        :param username: The name of the current user displayed in this chat session.
        """
        self.username = username
        self.receiver = MessageReceiverService(
            singletonSocket.get_instance(),
            callbacks={                                                 #A dictionary of methods to interact between threads
                'on_leave_request': self.leave_request_signal.emit,
                'on_leave_confirmation': self.leave_confirmation_signal.emit,
                'on_sent': lambda msg: self.update_message_status(msg['message_id'], 'Sent'),
                'on_received': lambda msg: self.update_message_status(msg['message_id'], 'Received'),
                'on_read': lambda msg: self.update_message_status(msg['message_id'], 'Read'),
                'on_new': self.process_incoming_message
            }
        )
        threading.Thread(target=self.receiver.receive_loop, daemon=True).start()

    ###########################################################################

    def close_connection(self, socket):
        """
        Closes the socket connection between the user and the server.
        """
        self.running = False
        socket.close()
        singletonSocket.reset_singleton()
        self.closed.emit() #Calls handlechatclosed. Connection made in client.py after the class was instanced

    ###########################################################################

    def handle_leave_request(self):
        """
        Closes the connection and returns to the home screen. 
        """
        self.close_connection(singletonSocket.get_instance())
        self.stacked_widget.setCurrentIndex(0)

    ###########################################################################

    def handle_leave_confirmation(self):
        """
        Closes the connection and returns to the home screen.
        Called when the other user has ended the connection. 
        """
        #TODO: Implement a message telling that the other user closed the chat
        self.close_connection(singletonSocket.get_instance())
        self.stacked_widget.setCurrentIndex(0)

    ###########################################################################

    def process_incoming_message(self, message):
        """
        Process an incoming message, sending a norification to the server telling that the message was received and dealing with the reading confirmation. 
        
        :param message: The message received. 
        """
        #Receiving confirmation
        message['message_type'] = MessageType.RECEIVE_RESPONSE.value
        socket = singletonSocket.get_instance()
        aes_key = singletonSocket.get_key()
        sending_data = (json.dumps(message) + '\n').encode('utf-8') #use \n to separate different messages in the socket buffer
        encryption.send_aes_message(socket, sending_data, aes_key)
        
        #TODO: add the option to disable reading confirmation
        #Reading confirmation
        if self.isActiveWindow():
            message['message_type'] = MessageType.READ_RESPONSE.value
            sending_data = (json.dumps(message) + '\n').encode('utf-8')
            encryption.send_aes_message(socket, sending_data, aes_key)
        else:
            self.unread_messages.append(message)

        self.new_message_signal.emit(message) #Puts the new message in the screen on handle_incoming_message

    ###########################################################################

    def handle_incoming_message(self, message):
        """
        Add an incoming message to the screen.

        :param message: The message received. 
        """
        widget = ChatMessageModel(message.get('user', 'Outro Usuário'), message['message'], message['timestamp'], False)
        self.add_message_to_layout(widget)

    ###########################################################################

    def handle_back_navigation(self):
        """
        Handles returning to the main window after pressing the back button in the chat screen. 
        """
        try:
            if singletonSocket.is_initialized():
                self.send_message(text='\\q')
                socket = singletonSocket.get_instance()
                socket.recv(1024)
                self.close_connection(socket)
        except Exception:
            pass

        self.stacked_widget.setCurrentIndex(0)

    ###########################################################################

    def update_message_status(self, message_id, status_text):
        """
        Updates the status of a message when it was sent, received or read.

        :param message_id: The unique identifier of the message.
        :param status_text: The string with the new status.
        """
        for i in range(self.chat_area.count()): #For every widget in the chat area
            widget = self.chat_area.itemAt(i).widget()
            if widget and widget.property("message_id") == message_id and widget.client_message: 
                current_text = widget.status_label.text()
                if " - " in current_text:
                    _, time_part = current_text.split(" - ", 1) #Keeps the timestamp, updating only the text
                    widget.status_label.setText(f"{status_text} - {time_part}")
                break

    ###########################################################################

    def send_message(self, text=None):
        """
        Updates the status of a message when it was sent, received or read. 

        :param text: The text of the message. Deafult is None.
        """
        text_html = text.strip() if text else self.input_field.toHtml().strip()
        text_plain = text.strip() if text else self.input_field.toPlainText().strip()

        if not text_plain:
            return

        message_id = str(uuid.uuid4())
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        message_widget = ChatMessageModel(self.username, text_html, timestamp, True)
        message_widget.setProperty("message_id", message_id)

        if text_plain == '\\q':
            msg_type = MessageType.LEAVE_REQUEST.value  
        else: 
            msg_type = MessageType.COMMON.value

        message_data = {
            "message_id": message_id,
            "user": self.username,
            "timestamp": timestamp,
            "message_type": msg_type,
            "message": text_html #So that the other user receive the formatted version
        }
        
        self.add_message_to_layout(message_widget)
        socket = singletonSocket.get_instance()
        aes_key = singletonSocket.get_key()
        sending_data = (json.dumps(message_data) + '\n').encode('utf-8')
        encryption.send_aes_message(socket, sending_data, aes_key)

        if text is None:
            self.input_field.clear()
            cursor = self.input_field.textCursor()
            cursor.setCharFormat(QTextCharFormat())
            self.input_field.setTextCursor(cursor)

    ###########################################################################

    def add_message_to_layout(self, message_widget):
        """
        Adds a message sent by the user to the chat screen.

        :param message_widget: The PyQt widget holding the new message widget.
        """
        scrollbar = self.scroll.verticalScrollBar()
        should_scroll =  ( scrollbar.value() == scrollbar.maximum() or not scrollbar.isVisible() ) 
        self.chat_area.insertWidget(self.chat_area.count() - 1, message_widget)

        if should_scroll: #Autoscroll to the bottom of the chat
            QTimer.singleShot(0, lambda: QTimer.singleShot(0, self.scroll_to_bottom))

    ###########################################################################

    def on_focus_changed(self):
        """
        Sends the reading confirmation when the screen becomes active.
        """
        if self.isActiveWindow():
            for msg in self.unread_messages[:]:
                msg['message_type'] = MessageType.READ_RESPONSE.value
                socket = singletonSocket.get_instance()
                aes_key = singletonSocket.get_key()
                sending_data = (json.dumps(msg) + '\n').encode('utf-8')
                encryption.send_aes_message(socket, sending_data, aes_key)
                self.unread_messages.remove(msg)

    ###########################################################################

    def scroll_to_bottom(self):
        """
        Autoscroll to the bottom of the chat
        """
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class SingleLineTextEdit(QTextEdit):
    """
    Class for the input field bottom bar of the chat screen.
    """
    returnPressed = pyqtSignal()

    ###########################################################################

    def __init__(self, *args, **kwargs):
        """
        Creates the input field bottom bar of the chat screen.
        """
        super().__init__(*args, **kwargs)

        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setPlaceholderText("Enter your message... Right-click in a selected text for formatting.")
        self.setFont(FontManager.PoppinsMedium)

    ###########################################################################

    def wheelEvent(self, event):
        #Ignore the wheel event
        event.ignore()

    ###########################################################################

    def keyPressEvent(self, event):
        """
        Handles the keyboard interaction. If enter is pressed, send the message; 
        otherwise, uses the default treatment of QTextEdit and reads the key pressed.
        """
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)

    ###########################################################################

    def contextMenuEvent(self, event):
        """
        Configures the context menu, opened whenever the right mouse button is clicked over a selected text.
        """
        cursor = self.textCursor()
        if cursor.hasSelection():
            menu = self.createStandardContextMenu()
            menu.setAttribute(Qt.WA_TranslucentBackground)
            menu.setWindowFlags(Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint | Qt.Popup)

            menu.setStyleSheet("""
                QMenu {
                    background-color: rgba(255, 255, 255, 255);
                    border: 2px solid #ccc;          
                    padding: 4px;
                    border-radius: 7px;
                }

                QMenu::item {
                    padding: 4px 8px;
                    background-color: transparent;
                    color: #333;
                    font-size: 14px;
                }

                QMenu::item:selected {
                    background-color: #0078d7;
                    color: white;
                    border-radius: 7px;
                }
            """)
            
            bold_action = menu.addAction("Bold")
            italic_action = menu.addAction("Italic")
            underline_action = menu.addAction("Underline")

            action = menu.exec_(event.globalPos())
            fmt = QTextCharFormat()

            if action == bold_action:
                current = cursor.charFormat().fontWeight()
                fmt.setFontWeight(QFont.Normal if current == QFont.Bold else QFont.Bold)
            elif action == italic_action:
                current = cursor.charFormat().fontItalic()
                fmt.setFontItalic(not current)
            elif action == underline_action:
                current = cursor.charFormat().fontUnderline()
                fmt.setFontUnderline(not current)

            cursor.mergeCharFormat(fmt)
        else:
            # If the right button is pressed without any function selected, the action will be ignored.
            event.ignore()
