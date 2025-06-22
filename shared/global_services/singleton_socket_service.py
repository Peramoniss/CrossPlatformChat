#|///////////////////////////////////////////////////////////////////////////|#
#| IMPORTS                                                                   |#
#|///////////////////////////////////////////////////////////////////////////|#

import threading



#|///////////////////////////////////////////////////////////////////////////|#
#| CLASS DEFINITION                                                          |#
#|///////////////////////////////////////////////////////////////////////////|#

class Socket:
    """
    Singleton class that manages a single instance of a network socket
    throughout the application's lifecycle.
    """
    
    __instance = None
    __lock = threading.Lock()
    __encryption_key = None

    #|///////////////////////////////////////////////////////////////////////|#

    #Talvez seja melhor só remover o inicializador?
    def __init__(self, network_socket):
        # """
        # Initializes the singleton with the provided socket instance.
        # This constructor is deprecated and should not be called directly — use `initialize()` instead.
        
        # :param network_socket: A valid socket object.
        # :raises Exception: If an instance already exists.
        # """
        # if Socket.__instance is not None:
        #     raise Exception("Socket instance already exists.")
        
        # self.network_socket = network_socket
        # Socket.__instance = self
        ...

    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def initialize(network_socket):
        """
        Initializes the singleton instance with a valid socket.
        Should be called only once during application startup, or after instance has been reset.

        :param network_socket: A valid socket object.
        :raises Exception: If the singleton is already initialized.
        """
        with Socket.__lock:
            print("AAAA")
            if Socket.__instance is None:
                print("BBBB")
                # Socket(network_socket)
                Socket.__instance = network_socket
            else:
                raise Exception("Socket has already been initialized.")

    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def get_instance():
        """
        Returns the singleton instance.

        :return: The Socket singleton instance.
        :raises Exception: If the singleton has not been initialized yet.
        """
        if Socket.__instance is None:
            raise Exception("Socket is not initialized.")
        return Socket.__instance

    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def is_initialized():
        """
        Checks whether the singleton has been initialized.

        :return: True if initialized, False otherwise.
        """
        return Socket.__instance is not None

    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def reset_singleton():
        """
        Resets the singleton instance.
        """
        Socket.__instance = None
        Socket.__encryption_key = None

    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def set_key(key):
        Socket.__encryption_key = key
    
    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def get_key():
        return Socket.__encryption_key