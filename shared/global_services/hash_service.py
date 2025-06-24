from sqids import Sqids 
import socket

sqids = Sqids(min_length=5)

def generate_connection_code(ip, port):
    """
        Returns an alphanumeric code to represent a set of ip and port values.

        :param ip: String ip address
        :param port: Integer port number.
        :return: The alphanumeric code generated.
    """
    ip_int = int.from_bytes(socket.inet_aton(ip), 'big') #convert big-endian bytes from a string ip to an int
    return sqids.encode([ip_int, port]) #generates the code

def decode_connection_code(codigo):
    """
        Returns the IP address and the port value from an alphanumeric code.

        :param code: String alphanumeric code.
        :return: Tuple where the first element is the IP address (str) and the second is the port number (int).
    """
    connection_data = sqids.decode(codigo)
    if connection_data is None or len(connection_data) != 2: #if decoded list couldn't be right
        raise ValueError("Invalid code")
    ip_int, port = connection_data 
    ip = socket.inet_ntoa(ip_int.to_bytes(4, 'big')) #converts the ip back
    return ip, port
