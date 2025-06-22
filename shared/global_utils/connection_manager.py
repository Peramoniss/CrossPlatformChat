#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import socket as sock



#|///////////////////////////////////////////////////////////////////////////|#
#| FUNCTION DEFINITION                                                       |#
#|///////////////////////////////////////////////////////////////////////////|#

def start_client():
    #global username
    network_socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

    # ip = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    # porta = int(sys.argv[2]) if len(sys.argv) > 2 else 65432
    ip = 'localhost'
    porta = 65432

    # username = input("Select an username: ")
    #username = 'TESTE'
    server_address = (ip, porta)
    #print(f"Connecting to {server_address}")
    network_socket.connect(server_address)

    try:
        data = network_socket.recv(1024)
        #print(f"Received: {data.decode()}")
        return network_socket
    except:
        network_socket.close()
