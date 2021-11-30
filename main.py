import time

from Server.ChatServer import ChatServer
from Logger.Logger import Logger

if __name__ == '__main__':
    Logger.get_logger().info('Welcome to UDP chat server!')
    server = ChatServer()
    Logger.get_logger().info('Hello, It is my server!')
    time.sleep(2)
    Logger.get_logger().info('Hello, It is my server2!')
    Logger.get_logger().info('Hello, It is my server3!')
    time.sleep(2)
    Logger.get_logger().close()
