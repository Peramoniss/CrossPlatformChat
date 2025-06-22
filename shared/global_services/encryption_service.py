from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

def create_aes_key():
    return AESGCM.generate_key(bit_length=256)

def aes_encrypt(key, data):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # Deve ser único por mensagem
    # Criptografar
    encrypted_data = aesgcm.encrypt(nonce, data, associated_data=None)
    return encrypted_data, nonce

def aes_decrypt(key, nonce, encrypted_data):
    aesgcm = AESGCM(key)
    # Descriptografar
    return aesgcm.decrypt(nonce, encrypted_data, associated_data=None)


def create_rsa_keys():
    # Cliente gera par de chaves assimétricas
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Exportar chave pública para enviar ao servidor
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ) 

    return private_key, public_pem, private_pem

#enviar aes_key para ca
def rsa_encrypt(public_pem, data):
    # Carregar chave pública recebida do cliente
    client_public_key = serialization.load_pem_public_key(public_pem)

    # Criptografar AES key
    encrypted_data = client_public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_data

#retorna a aes_key
def rsa_decrypt(private_key, encrypted_data):
    # encrypted_aes_key recebido do servidor
    data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return data

def send_aes_message(socket, sending_data, aes_key):
    encrypted_data, nonce = aes_encrypt(aes_key, sending_data)
    socket.sendall(nonce)
    socket.sendall(len(encrypted_data).to_bytes(4, 'big'))  # 4 bytes com tamanho do conteúdo
    socket.sendall(encrypted_data)  # conteúdo cifrado

def recv_all(socket, length):
    data = b''
    while len(data) < length:
        more = socket.recv(length - len(data))
        if not more:
            raise ConnectionResetError("Connection closed prematurely")
        data += more
    return data

def recv_aes_message(socket, aes_key):
    nonce = recv_all(socket, 12)  # 12 bytes exatos
    length_bytes = recv_all(socket, 4)
    encrypted_len = int.from_bytes(length_bytes, 'big')
    encrypted_data = recv_all(socket, encrypted_len)
    return aes_decrypt(aes_key, nonce, encrypted_data).decode('utf-8')