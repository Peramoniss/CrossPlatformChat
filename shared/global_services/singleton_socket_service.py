#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import threading



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class Socket:
    """
    Singleton, static class, that manages a single instance of a network socket
    throughout the chat session.
    Avoid instancing objects of this class.
    """
    
    __instance = None
    __lock = threading.Lock()
    __encryption_key = None #Also managing the encryption key for the session

    #|///////////////////////////////////////////////////////////////////////|#

    #A static class doesn't need to be instanced
    def __init__(self):
        ...

    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def initialize(network_socket):
        """
        Initializes the singleton instance with a valid socket.
        Should be called only once during application startup, or after the instance has been reset.

        :param network_socket: A valid socket object.
        :raises Exception: If the singleton is already initialized.
        """
        with Socket.__lock: #securing the usage from other threads 
            if Socket.__instance is None:
                Socket.__instance = network_socket
            else:
                raise Exception("Socket has already been initialized.")

    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def get_instance():
        """
        Returns the socket's singleton instance.

        :return: The socket's singleton instance.
        :raises Exception: If the singleton has not been initialized yet. Use initialize method before get_instance.
        """
        if Socket.__instance is None:
            raise Exception("Socket is not initialized.")
        return Socket.__instance

    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def is_initialized():
        """
        Checks whether or not the socket has been initialized.

        :return: True if initialized, False otherwise.
        """
        return Socket.__instance is not None

    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def reset_singleton():
        """
        Resets the socket's singleton instance.
        """
        Socket.__instance = None
        Socket.__encryption_key = None

    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def set_key(key):
        """
        Sets the encryption key.
        """
        Socket.__encryption_key = key
    
    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def get_key():
        """
        Returns the encryption key.
        
        :return: The encryption key.
        """
        return Socket.__encryption_key