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
    new_message_signal = pyqtSignal(object)
    closed = pyqtSignal()

    ###########################################################################

    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.unread_messages = []
        self.running = False

        self.new_message_signal.connect(self.handle_incoming_message)
        self.setup_user_interface()

        app = QApplication.instance()
        if app:
            app.focusChanged.connect(self.on_focus_changed)

    ###########################################################################

    def setup_user_interface(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setup_app_bar()
        self.setup_chat_area()
        self.setup_input_area()
        
    ###########################################################################

    def setup_app_bar(self):
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
        self.chat_area = QVBoxLayout()
        self.chat_area.addStretch(1)

        container = QWidget()
        container.setLayout(self.chat_area)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(container)
        self.scroll.setStyleSheet("background-color: #F0F0F0; border: none;")

        self.main_layout.addWidget(self.scroll)

    ###########################################################################

    def setup_input_area(self):
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
        self.username = username
        self.receiver = MessageReceiverService(
            singletonSocket.get_instance().network_socket,
            callbacks={
                'on_leave_request': self.handle_leave_request,
                'on_leave_confirmation': self.handle_leave_confirmation,
                'on_sent': lambda msg: self.update_message_status(msg['message_id'], 'Enviado'),
                'on_received': lambda msg: self.update_message_status(msg['message_id'], 'Recebido'),
                'on_read': lambda msg: self.update_message_status(msg['message_id'], 'Lido'),
                'on_new': self.process_incoming_message
            }
        )
        threading.Thread(target=self.receiver.receive_loop, daemon=True).start()

    ###########################################################################

    def close_connection(self, socket):
        singletonSocket.reset_singleton()
        self.running = False
        socket.close()
        self.closed.emit()

    ###########################################################################

    def handle_leave_request(self, message):
        self.close_connection(singletonSocket.get_instance().network_socket)
        self.stacked_widget.setCurrentIndex(0)

    ###########################################################################

    def handle_leave_confirmation(self, message):
        self.close_connection(singletonSocket.get_instance().network_socket)
        self.stacked_widget.setCurrentIndex(0)

    ###########################################################################

    def process_incoming_message(self, message):
        message['message_type'] = MessageType.RECEIVE_RESPONSE.value
        socket = singletonSocket.get_instance().network_socket
        socket.send((json.dumps(message) + '\n').encode('utf-8'))

        if self.isActiveWindow():
            message['message_type'] = MessageType.READ_RESPONSE.value
            socket.send((json.dumps(message) + '\n').encode('utf-8'))
        else:
            self.unread_messages.append(message)

        self.new_message_signal.emit(message)

    ###########################################################################

    def handle_incoming_message(self, message):
        widget = ChatMessageModel(message.get('user', 'Outro Usuário'), message['message'], message['timestamp'], False)
        self.add_message_to_layout(widget)

    ###########################################################################

    def handle_back_navigation(self):
        try:
            if singletonSocket.is_initialized():
                self.send_message(text_override='\\q')
                socket = singletonSocket.get_instance().network_socket
                self.close_connection(socket)
        except Exception:
            pass

        self.stacked_widget.setCurrentIndex(0)

    ###########################################################################

    def update_message_status(self, message_id, status_text):
        for i in range(self.chat_area.count()):
            widget = self.chat_area.itemAt(i).widget()
            if widget and widget.property("message_id") == message_id and widget.client_message:
                current_text = widget.status_label.text()
                if " - " in current_text:
                    _, time_part = current_text.split(" - ", 1)
                    widget.status_label.setText(f"{status_text} - {time_part}")
                break

    ###########################################################################

    def send_message(self, text_override=None):
        text_html = text_override.strip() if text_override else self.input_field.toHtml().strip()
        text_plain = text_override.strip() if text_override else self.input_field.toPlainText().strip()

        if not text_plain:
            return

        message_id = str(uuid.uuid4())
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        message_widget = ChatMessageModel(self.username, text_html, timestamp, True)
        message_widget.setProperty("message_id", message_id)

        msg_type = MessageType.LEAVE_REQUEST.value if text_plain == '\\q' else MessageType.COMMON.value

        message_data = {
            "message_id": message_id,
            "user": self.username,
            "timestamp": timestamp,
            "message_type": msg_type,
            "message": text_html
        }
        
        self.add_message_to_layout(message_widget)
        singletonSocket.get_instance().network_socket.send((json.dumps(message_data) + '\n').encode('utf-8'))

        if text_override is None:
            self.input_field.clear()
            cursor = self.input_field.textCursor()
            cursor.setCharFormat(QTextCharFormat())
            self.input_field.setTextCursor(cursor)

    ###########################################################################

    def add_message_to_layout(self, message_widget):
        scrollbar = self.scroll.verticalScrollBar()
        should_scroll = scrollbar.value() == scrollbar.maximum() or not scrollbar.isVisible()
        self.chat_area.insertWidget(self.chat_area.count() - 1, message_widget)

        if should_scroll:
            QTimer.singleShot(0, lambda: QTimer.singleShot(0, self.scroll_to_bottom))

    ###########################################################################

    def on_focus_changed(self):
        if self.isActiveWindow():
            for msg in self.unread_messages[:]:
                msg['message_type'] = MessageType.READ_RESPONSE.value
                socket = singletonSocket.get_instance().network_socket
                socket.send((json.dumps(msg) + '\n').encode('utf-8'))
                self.unread_messages.remove(msg)

    ###########################################################################

    def scroll_to_bottom(self):
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class SingleLineTextEdit(QTextEdit):
    returnPressed = pyqtSignal()

    ###########################################################################

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setPlaceholderText("Enter your message...")
        self.setFont(FontManager.PoppinsMedium)

    ###########################################################################

    def wheelEvent(self, event):
        event.ignore()

    ###########################################################################

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)

    ###########################################################################

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
