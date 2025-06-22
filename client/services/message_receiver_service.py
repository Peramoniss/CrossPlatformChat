#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import json
from shared.global_definitions import MessageType
from shared.global_services.singleton_socket_service import Socket as singleton_socket
import shared.global_services.encryption_service as encryption


#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

DELIMITER = '\n'
class MessageReceiverService:
    def __init__(self, socket, callbacks):
        self.socket = socket
        self.callbacks = callbacks
        self.running = True
        self.buffer = ""

    ###########################################################################

    def receive_loop(self):
        key = singleton_socket.get_key()
        try:
            while self.running:
                print("WAITING FOR THE RAPTURE")
                data = encryption.recv_aes_message(self.socket, key)
                print("WAITED FOR THE RAPTURE")
                self.buffer += data
                while DELIMITER in self.buffer:
                    msg_str, self.buffer = self.buffer.split(DELIMITER, 1)
                    msg_str = msg_str.strip()

                    if not msg_str:
                        continue

                    message = json.loads(msg_str)
                    self.handle_message(message)
        
        except:
            pass
    
    ###########################################################################

    def handle_message(self, message):
        msg_type = message['message_type']
        if msg_type == MessageType.LEAVE_REQUEST.value:
            self.callbacks['on_leave_request'](message)
        elif msg_type == MessageType.LEAVE_CONFIRMATION.value:
            self.callbacks['on_leave_confirmation'](message)
        elif msg_type == MessageType.SERVER_RESPONSE.value:
            self.callbacks['on_sent'](message)
        elif msg_type == MessageType.RECEIVE_RESPONSE.value:
            self.callbacks['on_received'](message)
        elif msg_type == MessageType.READ_RESPONSE.value:
            self.callbacks['on_read'](message)
        else:
            self.callbacks['on_new'](message)
