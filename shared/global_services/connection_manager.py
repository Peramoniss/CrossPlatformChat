#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import socket as sock

from shared.global_services import hash_service

#|///////////////////////////////////////////////////////////////////////////|#
#| FUNCTION DEFINITION                                                       |#
#|///////////////////////////////////////////////////////////////////////////|#

def start_client(code):
    #global username
    network_socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

    # ip = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    # porta = int(sys.argv[2]) if len(sys.argv) > 2 else 65432
    ip, port = hash_service.decode_connection_code(code)
    if ip is None:
        ip = 'localhost'
    if port is None:
        port = 65432

    # username = input("Select an username: ")
    #username = 'TESTE'
    server_address = (ip, port)
    #print(f"Connecting to {server_address}")
    network_socket.connect(server_address)

    try:
        data = network_socket.recv(1024)
        #print(f"Received: {data.decode()}")
        return network_socket
    except:
        network_socket.close()

#|///////////////////////////////////////////////////////////////////////|#

def get_local_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"
    finally:
        s.close()