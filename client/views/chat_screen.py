#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

from asyncio import sleep
import os
import json
import random
import threading
from PyQt5.QtCore import QSize, pyqtSignal
from shared.global_utils.font_manager import FontManager
from client.models.chat_message import ChatMessage
from shared.singleton_socket import Socket as singletonSocket
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
    QTimer
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
    
    #|///////////////////////////////////////////////////////////////////////|#

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        #|/// TOP BAR ///////////////////////////////////////////////////////|#

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


        #|/// TOP BAR: BACK BUTTON //////////////////////////////////////////|#

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


        #|/// TOP BAR: TITLE LABEL //////////////////////////////////////////|#

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


        #|/// SCROLL AREA ///////////////////////////////////////////////////|#

        self.chat_area = QVBoxLayout()
        self.chat_area.addStretch(1)
        container = QWidget()
        container.setLayout(self.chat_area)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(container)
        self.scroll.setStyleSheet("background-color: #e6e6e6; border: none;")
        main_layout.addWidget(self.scroll)

        
        #|/// BOTTOM BAR ////////////////////////////////////////////////////|#

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

    #|///////////////////////////////////////////////////////////////////////|#

    def start_connection(self, username):
        self.username = username
        receive_thread = threading.Thread(
            target = self.receive_messages, 
            args = [singletonSocket.get_instance().network_socket], 
            daemon=True
        )
        receive_thread.start()

    
    #|///////////////////////////////////////////////////////////////////////|#

    def close_connection(self, network_socket):
        print("Closing the connection")
        singletonSocket.reset_singleton()
        self.running = False
        network_socket.close()
        self.closed.emit()
    
    #|///////////////////////////////////////////////////////////////////////|#

    def handle_new_message(self, message):
        widget = ChatMessage(message.get('user', 'Outro Usuário'), message['message'], message['timestamp'], False)
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
        for i in range(self.chat_area.count()):  # último item é o 'stretch'
            widget = self.chat_area.itemAt(i).widget()
            if widget and widget.property("message_id") == message_id and widget.client_message:
                # Aqui você faz o que quiser: mudar cor, ícone, texto etc.
                widget.status_label.setText(str(message_text))
                break

    #|///////////////////////////////////////////////////////////////////////|#

    def receive_messages(self, network_socket):
        # global end
        self.running = True
        buffer = ""
        DELIMITER = '\n'
        try:
            while self.running: #doesn't need lock because python is thread safe when accessing boolean or integer variables
                data = network_socket.recv(1024).decode('utf-8')
                buffer += data
                # message_obj = json.loads(data.decode())
                new = True
                while DELIMITER in buffer:
                    message_str, buffer = buffer.split(DELIMITER, 1)
                    message_str = message_str.strip()
                    
                    if not message_str:  # Ignora strings vazias
                        continue
                    message_obj = json.loads(message_str)
                    if message_obj['message_type'] == MessageType.QUIT.value: #quit message from other user
                        print('Seu companheiro de chat desistiu da conversa :(')
                        self.close_connection(network_socket)
                        self.stacked_widget.setCurrentIndex(0)
                        break
                    elif message_obj['message_type'] == MessageType.QUIT_CONFIRM.value: #quit message recognizement
                        print('Escapou da coversa')
                        self.close_connection(network_socket)
                        self.stacked_widget.setCurrentIndex(0)
                        break
                    elif message_obj['message_type'] == MessageType.SERVER_RESPONSE.value: #system returning sent message
                        print('O servidor recebeu a mensagem enviada')
                        self.update_message_status(message_obj['message_id'], "Enviado")
                        sleep(0.5)
                        new = False
                    elif message_obj['message_type'] == MessageType.RECEIVE_RESPONSE.value: #system returning sent message
                        print('Seu companheiro de chat recebeu sua mensagem')
                        self.update_message_status(message_obj['message_id'], 'Recebido')
                        sleep(0.5)
                        new = False
                    elif message_obj['message_type'] == MessageType.READ_RESPONSE.value:
                        print('Seu companheiro de chat leu sua mensagem')
                        self.update_message_status(message_obj['message_id'], 'Lido')
                        sleep(0.5)
                        new = False

                    if new:
                        message_obj['message_type'] = MessageType.RECEIVE_RESPONSE.value
                        network_socket.send((json.dumps(message_obj) + '\n').encode('utf-8'))
                        if (self.isActiveWindow()):
                            message_obj['message_type'] = MessageType.READ_RESPONSE.value
                            network_socket.send((json.dumps(message_obj) + '\n').encode('utf-8'))
                        else:
                            self.unread_messages.append(message_obj)
                        self.new_message_signal.emit(message_obj)
        except Exception as e:
            print(f"Errinho {e}")
            print(message_obj)

    #|///////////////////////////////////////////////////////////////////////|#
    
    def send_message(self):
        text = self.input_field.toHtml().strip()
        text_aux = self.input_field.toPlainText().strip()
        if text_aux:
            message_id = random.randint(1000, 9999)
            timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
            message_widget = ChatMessage(self.username, text, timestamp, True)
            message_widget.setProperty("message_id", message_id)

            message_type = 0 #common message
            if text_aux == '\q':
                message_type = MessageType.QUIT.value #quit message

            message_json = {
                "message_id": message_id,  
                "user": self.username,
                "timestamp": timestamp,  
                # "read_status": 0,                          # 1 = lida
                "message_type": message_type, 
                "message": text_aux
            }
            singletonSocket.get_instance().network_socket.send((json.dumps(message_json ) + '\n').encode('utf-8')) #teste de envio
            self.add_message(message_widget)
            self.input_field.clear()

            # Resets text field formatting after submission.
            cursor = self.input_field.textCursor()
            default_format = QTextCharFormat()
            cursor.setCharFormat(default_format)
            self.input_field.setTextCursor(cursor)

    #|///////////////////////////////////////////////////////////////////////|#

    def add_message(self, message: ChatMessage):
        scrollbar = self.scroll.verticalScrollBar()
        is_at_bottom = scrollbar.value() == scrollbar.maximum()
        was_scroll_hidden = not scrollbar.isVisible() or scrollbar.maximum() == 0

        self.chat_area.insertWidget(self.chat_area.count() - 1, message)

        # Espera o layout atualizar antes de rolar.
        if is_at_bottom or was_scroll_hidden:
            QTimer.singleShot(0, lambda: QTimer.singleShot(0, self.scroll_to_bottom))

    #|///////////////////////////////////////////////////////////////////////|#

    def go_back(self):
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
