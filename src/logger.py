import logging
import os
from logging import Logger

from data import PATH_DATA


FORMAT = "%(asctime)s %(filename)s %(levelname)s: %(message)s"
LOG_PATH = os.path.join(PATH_DATA, "logs.log")


def get_console_handler(ch_level):
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(FORMAT)
    console_handler.setFormatter(console_formatter)

    return console_handler


def get_file_handler(fh_level):
    file_formatter = logging.Formatter(FORMAT)
    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setFormatter(file_formatter)

    return file_handler


def setup_logger(name: str = __name__,
                 fh_level: str | int = 1,
                 ch_level: str | int = 3,
                 log_level: str | int = 3) -> Logger:
    """
    Функция создает экземпляр Logger
    :param log_level: уровень логирования для логера
    :param ch_level: уровень логирования для консоли
    :param fh_level: уровень логирования для файла
    :param name: имя логера
    :return: Logger
    """
    file_handler = get_file_handler(fh_level)
    console_handler = get_console_handler(ch_level)

    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.setLevel(log_level)

    return logger
