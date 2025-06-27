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
    """
    A service destined to receive messages in the background while the main thread occupies itself handling the front-end. 
    """

    def __init__(self, socket, callbacks):
        """
        Starts the message receiving process.

        :param socket: Socket with the connection with the server.
        :param callbacks: A dictionary with functions to be performed in specific moments related to the connection flux. 
        """

        self.socket = socket
        self.callbacks = callbacks
        self.running = True
        self.buffer = ""

    ###########################################################################

    def receive_loop(self):
        """
        The main loop for receiving new messages.
        """

        key = singleton_socket.get_key()

        try:
            while self.running:
                data = encryption.recv_aes_message(self.socket, key)
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
        """
        Handles the different types of message, calling the function in the dictionary that relates to the message type. 
        """
        msg_type = message['message_type']
        if msg_type == MessageType.LEAVE_REQUEST.value:
            self.callbacks['on_leave_request']()
        elif msg_type == MessageType.LEAVE_CONFIRMATION.value:
            self.callbacks['on_leave_confirmation']()
        elif msg_type == MessageType.SERVER_RESPONSE.value:
            self.callbacks['on_sent'](message)
        elif msg_type == MessageType.RECEIVE_RESPONSE.value:
            self.callbacks['on_received'](message)
        elif msg_type == MessageType.READ_RESPONSE.value:
            self.callbacks['on_read'](message)
        else:
            self.callbacks['on_new'](message)
