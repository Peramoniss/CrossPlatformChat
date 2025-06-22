from sqids import Sqids 
import socket

sqids = Sqids(min_length=5)

def generate_connection_code(ip, port):
    ip_int = int.from_bytes(socket.inet_aton(ip), 'big') #Converte bytes big-endian de uma string de ip para um inteiro
    return sqids.encode([ip_int, port]) #sqids gera um código inteiro para isso

def decode_connection_code(codigo):
    connection_data = sqids.decode(codigo)
    if connection_data is None or len(connection_data) != 2:
        raise ValueError("Invalid code")
    ip_int, port = connection_data
    ip = socket.inet_ntoa(ip_int.to_bytes(4, 'big'))
    return ip, port
