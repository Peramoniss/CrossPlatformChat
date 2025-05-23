import json
import socket
import threading
import sys
import logging
from globals.messageType import MessageType

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
                print("Client disconnected.")
                break
                
            buffer += data
            ip, _ = client_socket.getpeername()
            
            # Processa todas as mensagens completas no buffer
            while DELIMITER in buffer:
                # Separa a primeira mensagem completa
                message_str, buffer = buffer.split(DELIMITER, 1)
                message_str = message_str.strip()  # Remove espaços em branco
                
                if not message_str:  # Ignora strings vazias
                    continue
                    
                try:
                    message_obj = json.loads(message_str)
                    print(f"{ip}: {message_obj.get('message', '')}")
                    
                    # Tratamento dos tipos de mensagem
                    if message_obj.get('message_type') == MessageType.QUIT.value:
                        other_client_socket.send((json.dumps(message_obj) + DELIMITER).encode('utf-8'))
                        message_obj['message_type'] = MessageType.QUIT_CONFIRM.value
                        client_socket.send((json.dumps(message_obj) + DELIMITER).encode('utf-8'))
                        break
                        
                    elif message_obj.get('message_type') == MessageType.RECEIVE_RESPONSE.value:
                        print(f"Atualizando status para {message_obj.get('read_status', '')}")
                        other_client_socket.send((json.dumps(message_obj) + DELIMITER).encode('utf-8'))
                        continue
                        
                    else:
                        # Encaminha para o outro cliente
                        other_client_socket.send((json.dumps(message_obj) + DELIMITER).encode('utf-8'))
                        message_obj['message_type'] = MessageType.SERVER_RESPONSE.value
                        client_socket.send((json.dumps(message_obj) + DELIMITER).encode('utf-8'))
                        
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON: {e}\nDados: {message_str[:100]}...")
                    continue
                    
        except (ConnectionResetError, UnicodeDecodeError) as e:
            print(f"Erro de conexão: {e}")
            break
            
    client_socket.close()
    other_client_socket.close()

# Start server and wait for connections
def start_server():
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if len(sys.argv) < 3:
        logging.warning(f"Nem todos os parâmetros foram definidos. Usando valores padrão.")
        logging.warning(f"Uso correto: {sys.argv[0]} <máscara> <porta>")
    
    # Default values if not passed via command line
    mask = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    porta = int(sys.argv[2]) if len(sys.argv) > 2 else 65432

    # Bind the socket to the address and port
    server_address = (mask, porta)
    server_socket.bind(server_address)

    # Listen for incoming connections (with a maximum queue of 2)
    server_socket.listen(2)
    print(f"Server is listening on {server_address}")

    # Accept exactly two connections
    connection1, client_address1 = server_socket.accept()
    print(f"Connection from {client_address1} established.")

    connection2, client_address2 = server_socket.accept()
    print(f"Connection from {client_address2} established.")

    # Start threads to handle each client connection
    thread1 = threading.Thread(target=handle_client, args=(connection1, connection2))
    thread2 = threading.Thread(target=handle_client, args=(connection2, connection1))

    thread1.start()
    thread2.start()

    # Wait for both threads to finish
    thread1.join()
    thread2.join()

    # Close the server socket when done
    print("Closing server.")
    server_socket.close()

if __name__ == "__main__":
    start_server()