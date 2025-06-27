#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import socket as sock

from shared.global_services import hash_service

#|///////////////////////////////////////////////////////////////////////////|#
#| FUNCTION DEFINITION                                                       |#
#|///////////////////////////////////////////////////////////////////////////|#

def start_client(code):
    """
    Starts a connection from the client with a server defined by the alphanumeric code.

    :param code: The alphanumeric code that represents the IP address and port to the server. 
    :return: a socket connection to the server.
    """
    network_socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

    ip, port = hash_service.decode_connection_code(code)
    if ip is None:
        ip = 'localhost'
    if port is None:
        port = 65432

    server_address = (ip, port)
    network_socket.connect(server_address)

    try:
        network_socket.recv(1024)
        return network_socket
    except:
        network_socket.close()

#|///////////////////////////////////////////////////////////////////////|#

def get_local_ip():
    """
    Connects temporarily to Google in order to get the IP address of the local machine.

    :return: The ip address of the local machine. 
    """
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"
    finally:
        s.close()