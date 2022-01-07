import time
from threading import Thread, Timer, Lock
from config import ENCODING, PORT, BUFFER_SIZE, TIME_OUT
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
        # Build UDP socket
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.client_lock = Lock()
        # Timer: check if the user is alive every minute
        self.__timer = Timer(TIME_OUT, self.__check_alive)

        self.socket.bind(('127.0.0.1', PORT))
        self.__timer.start()

        Logger.get_logger().info(f'Server listen 127.0.0.1:{PORT}')

    def __check_alive(self) -> None:
        """
        Check the user is alive
        Returns: None
        """
        offline_list = []
        current_time = time.time()

        self.client_lock.acquire()
        for user in self.user_set:
            if current_time - self.user_set[user][2] > TIME_OUT:
                offline_list.append(user)
        for offline in offline_list:
            Logger.get_logger().info(f'User {offline} was kicked out! Reason: time out.')
            self.user_set.pop(offline)
        self.client_lock.release()

        # New timer
        self.__timer = Timer(TIME_OUT, self.__check_alive)
        self.__timer.start()

    def __handle_login(self, param_list: list, ip_address: str, port: int) -> str:
        """
        Handle login command
        Args:
            param_list (list): parameter list of raw data
            ip_address (str): login user ip address
            port (int): login user port

        Returns: The message reply to login user.
        """
        reply_msg = PROTOCOL_STRING + LOGIN + CRLF
        user_name = param_list[0]
        self.client_lock.acquire()
        if user_name not in self.user_set:
            reply_msg += TRUE + CRLF
            reply_msg += LOGIN_SUCCESS
            self.user_set[user_name] = [ip_address, port, time.time()]
            Logger.get_logger().info(f'User {user_name} login! From {ip_address}:{port}.')
        else:
            reply_msg += FALSE + CRLF
            reply_msg += DUP_NAME
            Logger.get_logger().info(f'User {user_name} login failed! From {ip_address}:{port}.')
        self.client_lock.release()
        return reply_msg

    def __handle_message(self, param_list: list) -> str:
        """
        Handle message command
        Args:
            param_list (list): the parameter list of raw data.

        Returns: The message reply to sender.
        """

        # Build target msg and reply msg
        # target_msg will be sent to message target user.
        # reply_msg will be sent to sender, which is the message source user.
        target_msg = PROTOCOL_STRING + MESSAGE + CRLF
        reply_msg = PROTOCOL_STRING + REPLY_MSG + CRLF
        sender_name, receiver_name, message = param_list
        target_msg += sender_name + CRLF

        # Update last connection time
        self.client_lock.acquire()
        self.user_set[sender_name][2] = time.time()

        # Send type
        if receiver_name == PUBLIC:
            target_msg += PUBLIC + CRLF
        else:
            target_msg += PERSONAL + CRLF
        target_msg += message
        reply_msg += receiver_name + CRLF

        if receiver_name == PUBLIC:
            # If send to all user, send to each one.
            Logger.get_logger().info(
                f'User {sender_name} send message to ALL.'
            )
            for user in self.user_set:
                receiver_address, receiver_port, receiver_last_time = self.user_set[user]
                sender = socket(AF_INET, SOCK_DGRAM)
                sender.sendto(target_msg.encode(ENCODING), (receiver_address, receiver_port))
        else:
            if receiver_name not in self.user_set:
                # If the receiver user is offline, return error
                self.client_lock.release()
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
        self.client_lock.release()
        reply_msg += TRUE + CRLF + SEND_SUCCESS
        return reply_msg

    def __handle_check(self, para_list: list) -> str:
        """
        Handle check command
        Args:
            para_list (list): The parameter list of raw data

        Returns: The message reply to sender.
        """
        user_name = para_list[0]    
        self.client_lock.acquire()
        if user_name not in self.user_set:
            reply_msg = PROTOCOL_STRING + CHECK + CRLF + FALSE
            Logger.get_logger().info(f'User {user_name} check failed: User does not exist.')
        else:
            # Update last connection time
            self.user_set[user_name][2] = time.time()
            Logger.get_logger().info(f'User {user_name} check success.')
        self.client_lock.release()
        user_list_str = '\n'.join(self.user_set.keys())
        reply_msg = PROTOCOL_STRING + CHECK + CRLF + TRUE + CRLF + str(len(self.user_set.keys())) + CRLF + user_list_str

        return reply_msg

    @staticmethod
    def __decode_raw_data(data: bytes) -> tuple:
        """
        Decode raw data
        Args:
            data (bytes): raw data

        Returns: The command and parameter list of raw data, type is tuple: (command (str), param_list (list))
                 If the raw data is invalid, return (None, None)
        """
        decoded = data.decode(ENCODING)
        if not decoded.startswith(PROTOCOL_STRING):
            # Error: protocol string is not match
            return None, None
        command_and_params = decoded.strip(PROTOCOL_STRING).split(CRLF)

        command = command_and_params[0]
        param_list = command_and_params[1:]
        return command, param_list

    def handler(self, data: bytes, address: str) -> None:
        """handle the data received from client

        Args:
            data (bytes): The data received from client, encoded in utf-8
            address (tuple): The address of client, type is tuple: (ip_address, port)
        Returns: None
        """
        ip_address, port = address
        command, param_list = ChatServer.__decode_raw_data(data)

        if command is None or param_list is None:
            # Error: protocol string is not match
            Logger.get_logger().info(f'Error: protocol string is not match.')
            return

        reply_msg = PROTOCOL_STRING

        if command == LOGIN:
            reply_msg = self.__handle_login(param_list, ip_address, port)

        elif command == MESSAGE:
            reply_msg = self.__handle_message(param_list)

        elif command == CHECK:
            reply_msg = self.__handle_check(param_list)

        reply_socket = socket(AF_INET, SOCK_DGRAM)
        reply_socket.sendto(reply_msg.encode(ENCODING), (ip_address, port))

    def run(self) -> None:
        Logger.get_logger().info('Server start!')
        while True:
            data, client_address = self.socket.recvfrom(BUFFER_SIZE)
            handler_thread = Thread(target=self.handler, args=(data, client_address))
            handler_thread.start()
