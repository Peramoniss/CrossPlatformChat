import threading

class Socket:
    __instance = None
    soquete = None
    __lock = threading.Lock()

    @staticmethod
    def get_instance():
        return Socket.__instance

    def __init__(self, soquete):
        if Socket.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Socket.soquete = soquete
            Socket.__instance = self
            
    def reset_singleton():
        Socket.soquete = None
        Socket.__instance = None
