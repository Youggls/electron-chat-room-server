import time
from threading import Lock, Timer
from config import *


class Logger:
    logger = None

    def __init__(self, log_file_path, log2file_interval=5) -> None:
        self.__info_list_mutex = Lock()
        self.__info_list = []
        self.__log_file = open(log_file_path, mode='a+')
        self.__log2file_interval = log2file_interval
        self.__timer = Timer(self.__log2file_interval, self.__save2file_thread_worker)
        self.__timer.start()

    @property
    def __get_current_time(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def info(self, msg: str) -> None:
        self.__write_log(msg, 'INFO')

    def error(self, msg: str) -> None:
        self.__write_log(msg, 'ERROR')

    def warning(self, msg: str) -> None:
        self.__write_log(msg, 'WARNING')

    def debug(self, msg: str) -> None:
        self.__write_log(msg, 'DEBUG')

    def __write_log(self, msg: str, log_type: str) -> None:
        self.__info_list_mutex.acquire()
        self.__info_list.append(f'[{self.__get_current_time}][{log_type}]: {msg}')
        self.__info_list_mutex.release()
        print(self.__info_list[-1])

    def __save2file_without_mutex(self):
        save_info = f'[{self.__get_current_time}][INFO]: Begin to save log.'
        print(save_info)
        self.__info_list.append(save_info)
        for line in self.__info_list:
            self.__log_file.write(line + '\n')
        self.__info_list = []
        finish_info = f'[{self.__get_current_time}][INFO]: Log has been saved!.'
        print(finish_info)
        self.__info_list.append(finish_info)

    def __save2file_thread_worker(self) -> None:
        self.__info_list_mutex.acquire()
        self.__save2file_without_mutex()
        self.__info_list_mutex.release()
        self.__timer = Timer(self.__log2file_interval, self.__save2file_thread_worker)

    def close(self) -> None:
        self.__info_list_mutex.acquire()
        self.__save2file_without_mutex()
        self.__log_file.close()
        self.__info_list_mutex.release()

    @staticmethod
    def get_logger():
        if Logger.logger is None:
            Logger.logger = Logger(
                log_file_path=LOG_FILE_PATH,
                log2file_interval=LOG2FILE_INTERVAL
            )
        return Logger.logger
