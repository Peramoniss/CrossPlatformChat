#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import json
from shared.message_type import MessageType



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class MessageReceiverService:
    def __init__(self, socket, callbacks):
        self.socket = socket
        self.callbacks = callbacks
        self.running = True
        self.buffer = ""

    ###########################################################################

    def stop(self):
        self.running = False

    ###########################################################################

    def receive_loop(self):
        try:
            while self.running:
                data = self.socket.recv(1024).decode('utf-8')
                self.buffer += data
                while '\n' in self.buffer:
                    msg_str, self.buffer = self.buffer.split('\n', 1)
                    msg_str = msg_str.strip()

                    if not msg_str:
                        continue

                    message = json.loads(msg_str)
                    self.handle_message(message)
        
        except Exception as e:
            print(f"[MessageReceiver] Erro: {e}")
    
    ###########################################################################

    def handle_message(self, message):
        if message['message_type'] == MessageType.QUIT.value:
            self.callbacks['on_quit'](message)
        elif message['message_type'] == MessageType.SERVER_RESPONSE.value:
            self.callbacks['on_sent'](message)
        elif message['message_type'] == MessageType.RECEIVE_RESPONSE.value:
            self.callbacks['on_received'](message)
        elif message['message_type'] == MessageType.READ_RESPONSE.value:
            self.callbacks['on_read'](message)
        else:
            self.callbacks['on_new'](message)
