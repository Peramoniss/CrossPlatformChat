#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import json
import socket
import threading
import sys
import logging
from shared.global_definitions import MessageType
from shared.global_definitions import SERVER_LOGGING_MODE, LOG_FILE_PATH
import shared.global_services.connection_manager as connection_manager
import shared.global_services.encryption_service as encryption
import shared.global_services.hash_service as hasher

# Function to handle a client's communication
def handle_client(client_socket, other_client_socket, keys, index):
    """
    Method to handle a single client's connection to the server. Every client needs a thread, so the server can listen to them both simultaneously.
    
    :param client_socket: The socket connecting the client to the server.
    :param other_client_socket: The socket connecting the corresponding client to the server.
    :param keys: A list or tuple with the aes encryption keys for the encrypted connection. Should have exactly two keys, since it only handles private chats for now.
    :param index: The index of the client in the keys list, so the server knows which encryption key is used for the client and which is used by the corresponding client. 
    """
    aes_key = keys[index]
    other_aes_key = keys[1] 
    if index == 1: 
        other_aes_key = keys[0]

    buffer = ""
    DELIMITER = '\n'  # Newline as a delimiter between messages to avoid buffer issues
    
    while True:
        try:
            data = encryption.recv_aes_message(client_socket, aes_key)
            
            if not data:
                logging.info("Client disconnected.")
                break
                
            buffer += data # Adds data to a buffer
            ip, _ = client_socket.getpeername() # Gets the ip of the sender for logging purposes
            
            # Process every complete message in the buffer 
            while DELIMITER in buffer:
                message_str, buffer = buffer.split(DELIMITER, 1) # Separate each message and analyzes it separately
                message_str = message_str.strip()
                
                if not message_str:  # Ignore empty strings
                    continue
                    
                try:
                    message_obj = json.loads(message_str)
                    logging.info(f"Received from {message_obj.get('user', '')} of ip {ip}: {message_obj['message']}. TYPE - {MessageType(message_obj.get('message_type', '')).name}")
                    print(f"Received from {message_obj.get('user', '')} of ip {ip}: {message_obj['message']}. TYPE - {MessageType(message_obj.get('message_type', '')).name}")
                    
                    # Treats the different types of messages
                    if message_obj['message_type'] == MessageType.LEAVE_REQUEST.value: # When a user sends a \q
                        message_obj['message_type'] = MessageType.LEAVE_CONFIRMATION.value # Sends quitting message to the other user, so the connection is not forcedly closed 
                        sending_data = (json.dumps(message_obj) + DELIMITER).encode('utf-8')
                        encryption.send_aes_message(other_client_socket, sending_data, other_aes_key)
                        logging.info(f"Sent to {message_obj.get('user', '')} of ip {ip}: {message_obj.get('message', '')}. TYPE - {MessageType(message_obj.get('message_type', '')).name}")
                        # print("Sent to the other dude")
                        sending_data = (json.dumps(message_obj) + DELIMITER).encode('utf-8')
                        encryption.send_aes_message(client_socket, sending_data, aes_key)
                        logging.info(f"Sent {message_obj.get('user', '')} of ip {ip}: {message_obj.get('message', '')}. TYPE - {MessageType(message_obj.get('message_type', '')).name}")
                        # print("Received by the other dude")
                        return # Connection ended, can finish the thread
                        
                    elif message_obj.get('message_type') == MessageType.RECEIVE_RESPONSE.value: # When the client says they have received a message
                        sending_data = (json.dumps(message_obj) + DELIMITER).encode('utf-8') 
                        encryption.send_aes_message(other_client_socket, sending_data, other_aes_key) # Tells the other client that their message was received
                        continue
                        
                    else: # If it's a common message
                        sending_data = (json.dumps(message_obj) + DELIMITER).encode('utf-8')
                        encryption.send_aes_message(other_client_socket, sending_data, other_aes_key) #Forwards the message to the other client
                        # print("Sent to the other dude")
                        message_obj['message_type'] = MessageType.SERVER_RESPONSE.value #Sends a server response to the sender, so they know the message has sent succesfully
                        sending_data = (json.dumps(message_obj) + DELIMITER).encode('utf-8')
                        encryption.send_aes_message(client_socket, sending_data, aes_key)
                        # print("Advised it was sent to the other dude")
                        
                except json.JSONDecodeError as e:
                    logging.error(f"Failed to decode JSON: {e} | Data: {message_str[:100]}...")
                    continue
                    
        except (ConnectionResetError, UnicodeDecodeError) as e:
            logging.error(f"Connection error: {e}")
            break
            
    client_socket.close()
    other_client_socket.close()

def start_server():
    """
    Starts listening to the clients.
    """
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP/IP socket

    if len(sys.argv) < 3:
        print(f"Nem todos os parâmetros foram definidos. Usando valores padrão.")
        print(f"Uso correto: {sys.argv[0]} <máscara> <porta>")
    
    # Default values are assigned if not defined through command line
    mask = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 65432
    server_ip = connection_manager.get_local_ip()

    entering_code = hasher.generate_connection_code(server_ip, port)
    print(f"The code to join the current server is: {entering_code}")

    # Bind the socket to the mask and port
    server_address = (mask, port)
    server_socket.bind(server_address)

    # Listen for incoming connections (with a maximum queue of 2)
    server_socket.listen(2)
    logging.info(f"Server is listening on {server_address}")

    # Accept exactly two connections
    connection1, client_address1 = server_socket.accept()
    logging.info(f"Connection from {client_address1} established.")

    connection2, client_address2 = server_socket.accept()
    logging.info(f"Connection from {client_address2} established.")
    
    keys = []
    for curr_cli in [connection1, connection2]:
        curr_cli.send('Conexão estabelecida. Aguardando conversa...\n'.encode())
        aes_key = encryption.create_aes_key() #Generates symmetric aes key
        keys.append(aes_key)
        
        public_pem = curr_cli.recv(1024) #Receives the public rsa key of the client
        
        encrypted_aes = encryption.rsa_encrypt(public_pem, aes_key) #Sends aes symmetric key to the client through rsa asymmetric encrytion
        curr_cli.send(encrypted_aes)
        
    # Start threads to handle each client connection
    thread1 = threading.Thread(target=handle_client, args=(connection1, connection2, keys, 0))
    thread2 = threading.Thread(target=handle_client, args=(connection2, connection1, keys, 1))

    thread1.start()
    thread2.start()

    # Wait for both threads to end
    thread1.join()
    thread2.join()

    # Close the server socket when done
    logging.info("Server is shutting down.")
    print("Server is shutting down.")
    server_socket.close()

#|///////////////////////////////////////////////////////////////////////////|#
#| MAIN FUNCTION                                                             |#
#|///////////////////////////////////////////////////////////////////////////|#

if __name__ == "__main__":
    #Prepares the server to log
    if SERVER_LOGGING_MODE:
        log_formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
        file_handler.setFormatter(log_formatter)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
    else:
        logging.basicConfig(level=logging.CRITICAL)  # Ignora tudo exceto erros críticos

    #Start the server behaviour
    start_server()