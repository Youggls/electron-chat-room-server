from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM


class ChatServer:
    """
    Chat Server Class
    """
    def __init__(self) -> None:
        self.clients = []
        self.client_addresses = []


class ReceiverThread(Thread):
    """
    Listen port, receive data
    """
    def __init__(self, port) -> None:
        super(ReceiverThread).__init__()
        self.port = port
