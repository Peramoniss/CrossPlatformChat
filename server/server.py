#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import json
import socket
import threading
import sys
import logging
from shared.message_type import MessageType
from shared.global_definitions import SERVER_LOGGING_MODE, LOG_FILE_PATH



# Function to handle a client's communication
def handle_client(client_socket, other_client_socket):
    client_socket.send('Conexão estabelecida. Aguardando conversa...\n'.encode())
    buffer = ""
    DELIMITER = '\n'  # Usamos newline como delimitador
    
    while True:
        try:
            # Recebe dados e adiciona ao buffer
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                logging.info("Client disconnected.")
                break
                
            buffer += data
            ip, _ = client_socket.getpeername()
            
            # Processa todas as mensagens completas no buffer
            while DELIMITER in buffer:
                # Separa a primeira mensagem completa
                message_str, buffer = buffer.split(DELIMITER, 1)
                message_str = message_str.strip()
                
                if not message_str:  # Ignora strings vazias
                    continue
                    
                try:
                    message_obj = json.loads(message_str)
                    logging.info(f"Received from {message_obj.get('user', '')} of ip {ip}: {message_obj.get('message', '')}. TYPE - {MessageType(message_obj.get('message_type', '')).name}")
                    
                    # Tratamento dos tipos de mensagem
                    if message_obj.get('message_type') == MessageType.QUIT.value:
                        other_client_socket.send((json.dumps(message_obj) + DELIMITER).encode('utf-8'))
                        logging.info(f"Sent to {message_obj.get('user', '')} of ip {ip}: {message_obj.get('message', '')}. TYPE - {MessageType(message_obj.get('message_type', '')).name}")
                        message_obj['message_type'] = MessageType.QUIT_CONFIRM.value
                        client_socket.send((json.dumps(message_obj) + DELIMITER).encode('utf-8'))
                        logging.info(f"Sent {message_obj.get('user', '')} of ip {ip}: {message_obj.get('message', '')}. TYPE - {MessageType(message_obj.get('message_type', '')).name}")
                        break
                        
                    elif message_obj.get('message_type') == MessageType.RECEIVE_RESPONSE.value:
                        #logging.info(f"Updating read status to: {message_obj.get('read_status', '')}")
                        other_client_socket.send((json.dumps(message_obj) + DELIMITER).encode('utf-8'))
                        continue
                        
                    else:
                        # Encaminha para o outro cliente
                        other_client_socket.send((json.dumps(message_obj) + DELIMITER).encode('utf-8'))
                        message_obj['message_type'] = MessageType.SERVER_RESPONSE.value
                        client_socket.send((json.dumps(message_obj) + DELIMITER).encode('utf-8'))
                        
                except json.JSONDecodeError as e:
                    logging.error(f"Failed to decode JSON: {e} | Data: {message_str[:100]}...")
                    continue
                    
        except (ConnectionResetError, UnicodeDecodeError) as e:
            logging.error(f"Connection error: {e}")
            break
            
    client_socket.close()
    other_client_socket.close()




# Start server and wait for connections
def start_server():
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if len(sys.argv) < 3:
        #logging.warning(f"Nem todos os parâmetros foram definidos. Usando valores padrão.")
        #logging.warning(f"Uso correto: {sys.argv[0]} <máscara> <porta>")
        ...
    
    # Default values if not passed via command line
    mask = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    porta = int(sys.argv[2]) if len(sys.argv) > 2 else 65432

    # Bind the socket to the address and port
    server_address = (mask, porta)
    server_socket.bind(server_address)

    # Listen for incoming connections (with a maximum queue of 2)
    server_socket.listen(2)
    logging.info(f"Server is listening on {server_address}")

    # Accept exactly two connections
    connection1, client_address1 = server_socket.accept()
    logging.info(f"Connection from {client_address1} established.")

    connection2, client_address2 = server_socket.accept()
    logging.info(f"Connection from {client_address2} established.")

    # Start threads to handle each client connection
    thread1 = threading.Thread(target=handle_client, args=(connection1, connection2))
    thread2 = threading.Thread(target=handle_client, args=(connection2, connection1))

    thread1.start()
    thread2.start()

    # Wait for both threads to finish
    thread1.join()
    thread2.join()

    # Close the server socket when done
    logging.info("Server is shutting down.")
    server_socket.close()



#|///////////////////////////////////////////////////////////////////////////|#
#| MAIN FUNCTION                                                             |#
#|///////////////////////////////////////////////////////////////////////////|#

if __name__ == "__main__":
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

    start_server()