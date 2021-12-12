from Server.ChatServer import ChatServer
from Logger.Logger import Logger

if __name__ == '__main__':
    try:
        cs = ChatServer()
        cs.start()
        cs.join()
    except Exception as e:
        Logger.get_logger().error(str(e))
        Logger.get_logger().close()
