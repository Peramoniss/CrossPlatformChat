#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

from asyncio import sleep
import os
import json
import random
import threading
from client.models.chat_message_model import ChatMessageModel
from client.services.message_receiver_service import MessageReceiverService
from shared.global_utils.font_manager import FontManager
from shared.global_services.singleton_socket import Socket as singletonSocket
from shared.message_type import MessageType 

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
    new_message_signal = pyqtSignal(object)
    closed = pyqtSignal()

    ###########################################################################

    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()
        self.running = False

        self.new_message_signal.connect(self.handle_new_message)        
        self.unread_messages = []
        app = QApplication.instance()

        if app is not None:
            app.focusChanged.connect(self.on_focus_changed)
    
    ###########################################################################

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        app_bar_container = QFrame()
        app_bar_container.setStyleSheet("background: transparent; ")
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

        back_button = QPushButton()
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        icon_path = os.path.join(BASE_DIR, "shared", "global_assets", "icons", "arrow-back.svg")
        back_button.setIcon(QIcon(icon_path))
        back_button.setIconSize(QSize(20, 20))
        back_button.setStyleSheet("""
            background-color: transparent; 
            border: none;
        """)
        back_button.setFixedSize(40, 40)
        back_button.clicked.connect(self.go_back)

        title_label = QLabel("BlaBlaBla Chat")
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
        main_layout.addWidget(app_bar_container)

        self.chat_area = QVBoxLayout()
        self.chat_area.addStretch(1)
        container = QWidget()
        container.setLayout(self.chat_area)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(container)
        self.scroll.setStyleSheet("background-color: #e6e6e6; border: none;")
        main_layout.addWidget(self.scroll)

        input_layout = QHBoxLayout()
        self.input_field = SingleLineTextEdit()
        self.input_field.returnPressed.connect(self.send_message)
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        
        common_style = """
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

        send_button.setStyleSheet(common_style)
        send_button.setFixedHeight(48)
        send_button.setFont(FontManager.PoppinsMedium)
        
        self.input_field.setStyleSheet(common_style)
        self.input_field.setFixedHeight(48)
        self.input_field.setFont(FontManager.PoppinsMedium)

        inner_layout.setAlignment(Qt.AlignVCenter)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_button)

        input_frame = QFrame()
        input_frame.setLayout(input_layout)
        input_frame.setStyleSheet("""
            padding: 5px;
            background-color: white;
            border-top: 1px solid rgba(0, 0, 0, 40);
        """)
        
        main_layout.addWidget(input_frame)

    ###########################################################################

    def start_connection(self, username):
        self.username = username
        self.receiver = MessageReceiverService(
            singletonSocket.get_instance().network_socket,
            callbacks = {
                'on_quit': lambda msg_obj: self.handle_quit(msg_obj),
                'on_sent': lambda msg_obj: self.update_message_status(msg_obj['message_id'], 'Enviado'),
                'on_received': lambda msg_obj: self.update_message_status(msg_obj['message_id'], 'Recebido'),
                'on_read': lambda msg_obj: self.update_message_status(msg_obj['message_id'], 'Lido'),
                'on_new': lambda msg_obj: self._handle_new_incoming_message(msg_obj)
            }
        )
        thread = threading.Thread(target=self.receiver.receive_loop, daemon=True)
        thread.start()
    
    ###########################################################################

    def close_connection(self, network_socket):
        singletonSocket.reset_singleton()
        self.running = False
        network_socket.close()
        self.closed.emit()
    
    ###########################################################################

    def _handle_new_incoming_message(self, message):
        message['message_type'] = MessageType.RECEIVE_RESPONSE.value
        singletonSocket.get_instance().network_socket.send(
            (json.dumps(message) + '\n').encode('utf-8')
        )

        if self.isActiveWindow():
            message['message_type'] = MessageType.READ_RESPONSE.value
            singletonSocket.get_instance().network_socket.send(
                (json.dumps(message) + '\n').encode('utf-8')
            )
        else:
            self.unread_messages.append(message)

        self.new_message_signal.emit(message)
    
    #|///////////////////////////////////////////////////////////////////////|#

    def handle_new_message(self, message):
        widget = ChatMessageModel(message.get('user', 'Outro Usuário'), message['message'], message['timestamp'], False)
        self.add_message(widget)

    #|///////////////////////////////////////////////////////////////////////|#

    def on_focus_changed(self):
        if self.isActiveWindow():
            for message in self.unread_messages[:]:
                message['message_type'] = MessageType.READ_RESPONSE.value
                singletonSocket.get_instance().network_socket.send((json.dumps(message) + '\n').encode('utf-8'))
                self.unread_messages.remove(message)

    #|///////////////////////////////////////////////////////////////////////|#

    def update_message_status(self, message_id, message_text):
        for i in range(self.chat_area.count()):
            widget = self.chat_area.itemAt(i).widget()
            if widget and widget.property("message_id") == message_id and widget.client_message:
                widget.status_label.setText(str(message_text))
                break

    #|///////////////////////////////////////////////////////////////////////|#
    
    def send_message(self, text_override=None):
        if text_override:
            text = text_aux = text_override.strip()
        else:
            text = self.input_field.toHtml().strip()
            text_aux = self.input_field.toPlainText().strip()

        if text_aux:
            message_id = random.randint(1000, 9999)
            timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
            message_widget = ChatMessageModel(self.username, text, timestamp, True)
            message_widget.setProperty("message_id", message_id)
            message_type = MessageType.COMMON.value

            if text_aux == '\q':
                message_type = MessageType.QUIT.value

            message_json = {
                "message_id": message_id,
                "user": self.username,
                "timestamp": timestamp,
                "message_type": message_type,
                "message": text_aux
            }

            singletonSocket.get_instance().network_socket.send(
                (json.dumps(message_json) + '\n').encode('utf-8')
            )

            self.add_message(message_widget)

            # Limpa o campo de entrada somente se o texto veio do input_field
            if text_override is None:
                self.input_field.clear()
                cursor = self.input_field.textCursor()
                default_format = QTextCharFormat()
                cursor.setCharFormat(default_format)
                self.input_field.setTextCursor(cursor)


    #|///////////////////////////////////////////////////////////////////////|#

    def add_message(self, message: ChatMessageModel):
        scrollbar = self.scroll.verticalScrollBar()
        is_at_bottom = scrollbar.value() == scrollbar.maximum()
        was_scroll_hidden = not scrollbar.isVisible() or scrollbar.maximum() == 0
        self.chat_area.insertWidget(self.chat_area.count() - 1, message)

        if is_at_bottom or was_scroll_hidden:
            QTimer.singleShot(0, lambda: QTimer.singleShot(0, self.scroll_to_bottom))

    #|///////////////////////////////////////////////////////////////////////|#

    def go_back(self):
        try:
            if singletonSocket.is_initialized():
                self.send_message(text_override = '\q')
                socket_instance = singletonSocket.get_instance()
                self.close_connection(socket_instance.network_socket)
        except:
            pass

        self.stacked_widget.setCurrentIndex(0)

    #|///////////////////////////////////////////////////////////////////////|#
    
    def scroll_to_bottom(self):
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class SingleLineTextEdit(QTextEdit):
    returnPressed = pyqtSignal()

    #|///////////////////////////////////////////////////////////////////////|#

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setPlaceholderText("Enter your message...")
        self.setFont(FontManager.PoppinsMedium)

    #|///////////////////////////////////////////////////////////////////////|#

    def wheelEvent(self, event):
        event.ignore()

    #|///////////////////////////////////////////////////////////////////////|#

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)

    #|///////////////////////////////////////////////////////////////////////|#

    def contextMenuEvent(self, event):
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
            # If the right button is pressed without any 
            # text selected, the action will be ignored.
            event.ignore()
