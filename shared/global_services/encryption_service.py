import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

def create_aes_key():
    """
    Creates a symmetric cryptography aes key
    
    :return: The 256 bits aes key
    """
    return AESGCM.generate_key(bit_length=256)

def aes_encrypt(key, data):
    """
    Encrypts data using aes cryptography.

    :param key: The aes key for cryptographing the data.
    :param data: Data to be cryptographed.
    :return: A tuple consisting of the encrypted data at index 0, and the nonce at index 1.
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # Deve ser único por mensagem
    # Criptografar
    encrypted_data = aesgcm.encrypt(nonce, data, associated_data=None)
    return encrypted_data, nonce

def aes_decrypt(key, nonce, encrypted_data):
    """
    Decrypts aes-encrypted data.
    
    :param key: The aes key for decrypting the data.
    :param nonce: The nonce for decrypting the data.
    :param nonce: The encrypted data for decryption.

    :return: The decrypted data.
    """
    aesgcm = AESGCM(key)
    # Descriptografar
    return aesgcm.decrypt(nonce, encrypted_data, associated_data=None)


def create_rsa_keys():
    """
    Creates asymmetric rsa keys for exchanging the aes keys. 
    Should be used by the client, who will send the public key to the server and only the client should be able to decrypt the aes key using the private key. 
    
    :return: A touple consisting of the private key at index 0 and the public PEM at index 1. 
    """
    # Client creates private and public keys
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Client generates package for sending the public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key, public_pem


"""
Asymmetric encryption is used unidrectionally. The private key can encrypt data that only the public key can decrypt, and vice-versa. 
Therefore, the public key can be sent through a channel with no worries, because it wil only serve for the receiver to encrypt data that can only be decrypted by the public key
Then, the communication will be unidirectional: the users with the public key will send encrypted data, and the users with the private key will never send anything, since it could be decrypted by the public key, which could be intercepted. 
That's why asymmetric encryption is mostly used to pass the key for a symmetric encryption - it would make no sense to send around the web content that can easily be decrypted by a man-in-the-middle. So, the user with the private key only receives data (in this case).
"""

def rsa_encrypt(public_pem, data):
    """
    Encrypts data using rsa. 
    Should be used by the server to encrypt the aes key using the public pem.

    :param public_pem: The PEM data sent by the client containing the public key.
    :param data: The plain data to be encrypted.
    :return: The rsa encrypted data.
    """
    # Converts the public pem to a public key 
    client_public_key = serialization.load_pem_public_key(public_pem)

    # Encrypts the aes key
    encrypted_data = client_public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_data

def rsa_decrypt(private_key, encrypted_data):
    """
    Decrypts data encrypted with rsa.
    Should be used by the client to decrypt the aes key sent encrypted by the server.
 
    :return: The plain, decrypted data.
    """
    
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
    """
    Encrypts data using aes and sends it through a socket.

    :param socket: The socket connection in which the data will be sent.
    :param sending_data: The plain data to be sent.  
    :param aes_key: The aes key to encrypt the data.
    """

    encrypted_data, nonce = aes_encrypt(aes_key, sending_data)
    socket.sendall(nonce)
    socket.sendall(len(encrypted_data).to_bytes(4, 'big'))  # 4 bytes com tamanho do conteúdo
    socket.sendall(encrypted_data)  # conteúdo cifrado

def recv_all(socket, length):
    """
    Receive a determined length of bytes through a socket, guaranteeing the recovery of all of these bytes.

    :param socket: The socket connection.
    :length: The length of the data to be recovered, in bytes. 

    :return: The length bytes data.
    """
    data = b''
    while len(data) < length:
        more = socket.recv(length - len(data))
        if not more:
            raise ConnectionResetError("Connection closed prematurely")
        data += more
    return data

def recv_aes_message(socket, aes_key):
    """
    Receive a message encrypted with aes and decrypts it.

    :param socket: The socket connection.
    :param aes_key: The aes key for decryption of the data.

    :return: The decrypted data.
    """
    nonce = recv_all(socket, 12)  # Receiver exactly 12 bytes, guaranteeing to get the nonce
    length_bytes = recv_all(socket, 4)
    encrypted_len = int.from_bytes(length_bytes, 'big')
    encrypted_data = recv_all(socket, encrypted_len)
    return aes_decrypt(aes_key, nonce, encrypted_data).decode('utf-8')