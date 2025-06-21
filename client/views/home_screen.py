#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import os
from shared.global_services.singleton_socket import Socket
from client.views.chat_screen import ChatScreen
from shared.global_utils.connection_manager import start_client
from shared.global_utils.font_manager import FontManager
from PyQt5.QtGui import QPainter, QPainterPath, QLinearGradient, QRadialGradient, QConicalGradient, QColor, QFontMetrics

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QSpacerItem, QSizePolicy, QProgressBar, QGraphicsDropShadowEffect
)

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QBrush
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QImage, QPixmap, QBrush



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class ConnectionThread(QThread):
    connected = pyqtSignal(object)
    error = pyqtSignal(Exception)

    def __init__(self):
        super().__init__()
        self._is_running = True

    def run(self):
        try:
            # Simulando uma espera ou tentativa de conexão com checagem periódica
            # Aqui você deve adaptar start_client para ser "cancelável"
            # Se start_client for bloqueante, você precisa adaptar ele também
            # Para exemplo, um loop checando o flag:

            for _ in range(50):  # Exemplo: tenta por 5 segundos (50 * 0.1)
                if not self._is_running:
                    # Thread foi cancelada
                    return
                self.msleep(100)  # 100ms

            if not self._is_running:
                return

            network_socket = start_client()
            if not self._is_running:
                return

            self.connected.emit(network_socket)
        except Exception as e:
            self.error.emit(e)

    def stop(self):
        self._is_running = False



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class GradientLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.gradient_colors = [(0, QColor(18, 62, 205)),
                                (1, QColor(40, 115, 246))]

    def setGradientColors(self, colors):
        self.gradient_colors = colors
        self.update()

    def paintEvent(self, event):
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

        # Calcula posição do texto
        metrics = QFontMetrics(font)
        text_rect = metrics.boundingRect(text)

        x = 0  # Alinhado à esquerda
        y = (rect.height() + text_rect.height()) / 2 - metrics.descent()

        # Cria path com o texto
        path = QPainterPath()
        path.addText(x, y, font, text)

        # Aplica o gradiente como brush e desenha o path
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class HomeScreen(QWidget):
    def __init__(self, stacked_widget, main_window):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.main_window = main_window
        self.thread = None

        # Layout principal vertical com padding nas bordas
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)
        self.setLayout(self.main_layout)
        self.setFont(FontManager.PoppinsSemiBold)

        # Topo com o texto "Bla Bla Bla" e "Chat"
        self.top_widget = QWidget()
        self.top_layout = QVBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        self.top_widget.setLayout(self.top_layout)

        self.top_layout.addStretch()

        # Novo container para os dois labels empilhados verticalmente
        text_column = QWidget()
        text_column_layout = QVBoxLayout()
        text_column_layout.setContentsMargins(0, 0, 0, 0)
        text_column_layout.setSpacing(0)  # espaçamento pequeno e positivo
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

        # Container branco que vai ocupar os 2/3 inferiores
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

        # Campo para código da sala
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

        # Campo de nome de usuário
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

        # Botão de entrada
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

        # Botão de cancelar (inicialmente oculto)
        self.cancel_button = QPushButton("Cancelar")
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

        # Mensagem de erro (oculta por padrão)
        self.error_label = QLabel("Username is required.")
        self.error_label.setStyleSheet("color: red; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        self.right_layout.addWidget(self.error_label)

        # Barra de progresso na parte inferior
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
        self.update()

    #|///////////////////////////////////////////////////////////////////////|#

    def go_to_chat(self):
        username = self.username_input.text().strip()

        if not username:
            self.error_label.show()
            return

        self.error_label.hide()
        self.button.setEnabled(False)
        self.username_input.setEnabled(False)
        self.room_code_input.setEnabled(False)
        self.progress_bar.show()

        self.cancel_button.show()

        self.thread = ConnectionThread()
        self.thread.connected.connect(self.on_connected)
        self.thread.error.connect(self.on_connection_error)
        self.thread.start()
    
    #|///////////////////////////////////////////////////////////////////////|#

    def cancel_connection(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()

        self.progress_bar.hide()
        self.cancel_button.hide()
        self.button.setEnabled(True)
        self.username_input.setEnabled(True)
        self.room_code_input.setEnabled(True)
        self.error_label.hide()
    
    #|///////////////////////////////////////////////////////////////////////|#

    def on_connected(self, network_socket):
        self.progress_bar.hide()
        self.cancel_button.hide()
        self.button.setEnabled(True)
        self.username_input.setEnabled(True)
        self.room_code_input.setEnabled(True)

        Socket(network_socket)
        self.main_window.chat_screen.start_connection(self.username_input.text().strip())
        self.main_window.stacked_widget.setCurrentIndex(1)
    
    #|///////////////////////////////////////////////////////////////////////|#

    def on_connection_error(self, exception):
        self.progress_bar.hide()
        self.cancel_button.hide()
        self.button.setEnabled(True)
        self.username_input.setEnabled(True)
        self.room_code_input.setEnabled(True)
        self.error_label.setText(f"Erro de conexão: {str(exception)}")
        self.error_label.show()

    #|///////////////////////////////////////////////////////////////////////|#
    
    def create_tiled_svg_brush(self, svg_path):
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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fundo colorido
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        if self.background_brush:
            painter.setOpacity(0.05)
            painter.fillRect(self.rect(), self.background_brush)
            painter.setOpacity(1.0)

        super().paintEvent(event)
