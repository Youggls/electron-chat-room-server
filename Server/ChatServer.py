import time
from threading import Thread, Timer, Lock
from config import ENCODING, PORT, BUFFER_SIZE
from socket import socket, AF_INET, SOCK_DGRAM
from Logger.Logger import Logger
from .Constants import *


class ChatServer(Thread):
    """
    Chat Server Class
    """
    def __init__(self) -> None:
        super().__init__()
        # User list, each entry contains three item: ip address, port, last connection time
        self.user_set = {}
        self.port = PORT
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', PORT))
        self.client_lock = Lock()

    def __handle_login(self, param_list, ip_address, port) -> str:
        reply_msg = PROTOCOL_STRING + LOGIN + CRLF
        user_name = param_list[0]
        if user_name not in self.user_set:
            reply_msg += TRUE + CRLF
            reply_msg += LOGIN_SUCCESS
            self.user_set[user_name] = [ip_address, port, time.time()]
            Logger.get_logger().info(f'User {user_name} login! From {ip_address}:{port}.')
        else:
            reply_msg += FALSE + CRLF
            reply_msg += DUP_NAME
            Logger.get_logger().info(f'User {user_name} login failed! From {ip_address}:{port}.')
        return reply_msg

    def __handle_message(self, param_list) -> str:
        """
        Handle message command
        Args:
            param_list: the parameter list of raw data.

        Returns: The message reply to sender.
        """
        target_msg = PROTOCOL_STRING + MESSAGE + CRLF
        reply_msg = PROTOCOL_STRING + REPLY_MSG + CRLF
        sender_name, receiver_name, message = param_list
        target_msg += sender_name + CRLF

        # Update last connection time
        self.user_set[sender_name][2] = time.time()

        if receiver_name == ALL:
            target_msg += PUBLIC + CRLF
        else:
            target_msg += PERSONAL + CRLF

        target_msg += message
        if receiver_name == ALL:
            Logger.get_logger().info(
                f'User {sender_name} send message to ALL.'
            )
            for user in self.user_set:
                receiver_address, receiver_port, receiver_last_time = self.user_set[user]
                sender = socket(AF_INET, SOCK_DGRAM)
                sender.sendto(target_msg.encode(ENCODING), (receiver_address, receiver_port))
        else:
            if receiver_name not in self.user_set:
                Logger.get_logger().info(
                    f'User {sender_name} send message to {receiver_name} failed: {RECEIVER_OFF}'
                )
                return reply_msg + FALSE + CRLF + RECEIVER_OFF
            Logger.get_logger().info(
                f'User {sender_name} send message to {receiver_name}, length is {len(message)}'
            )
            receiver_address, receiver_port, receiver_last_time = self.user_set[receiver_name]
            sender = socket(AF_INET, SOCK_DGRAM)
            sender.sendto(target_msg.encode(ENCODING), (receiver_address, receiver_port))
        reply_msg += TRUE + CRLF + SEND_SUCCESS
        return reply_msg

    def __handle_check(self, para_list):
        user_name = para_list[0]
        # Update last connection time
        self.user_set[user_name][2] = time.time()
        reply_msg = PROTOCOL_STRING + CHECK + CRLF

        # Get the current user number
        reply_msg += str(len(self.user_set))
        return reply_msg

    def handler(self, data, address):
        decoded = data.decode(ENCODING)
        ip_address, port = address
        message_detail = decoded.strip(PROTOCOL_STRING)
        command_and_params = message_detail.split(CRLF)
        command = command_and_params[0]
        param_list = command_and_params[1:]
        reply_msg = PROTOCOL_STRING

        if command == LOGIN:
            reply_msg = self.__handle_login(param_list, ip_address, port)

        elif command == MESSAGE:
            reply_msg = self.__handle_message(param_list)

        reply_socket = socket(AF_INET, SOCK_DGRAM)
        reply_socket.sendto(reply_msg.encode(ENCODING), (ip_address, port))

    def run(self) -> None:
        while True:
            data, client_address = self.socket.recvfrom(BUFFER_SIZE)
            handler_thread = Thread(target=self.handler, args=(data, client_address))
            handler_thread.start()
            # self.handler(data, client_address)
