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

    #|///////////////////////////////////////////////////////////////////////|#

    def __init__(self, network_socket):
        """
        Initializes the singleton with the provided socket instance.
        This constructor should not be called directly—use `initialize()` instead.
        
        :param network_socket: A valid socket object.
        :raises Exception: If an instance already exists.
        """
        if Socket.__instance is not None:
            raise Exception("Socket instance already exists.")
        
        self.network_socket = network_socket
        Socket.__instance = self

    #|///////////////////////////////////////////////////////////////////////|#

    @staticmethod
    def initialize(network_socket):
        """
        Initializes the singleton instance with a valid socket.
        Should be called only once during application startup.

        :param network_socket: A valid socket object.
        :raises Exception: If the singleton is already initialized.
        """
        with Socket.__lock:
            if Socket.__instance is None:
                Socket(network_socket)
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
