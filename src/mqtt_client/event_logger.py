"""
Создание логера для обработки событий.
Важные сообщения и ошибки записываются в соответствующие файлы.
Остальные сообщения выводятся в консоль.
 """
import logging
import sys
import os
from .common_func import get_full_path


FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
SHORT_FORMATTER = logging.Formatter("%(levelname)s — %(message)s")
EVENT_LOG_FILE = get_full_path("logs/events.log")
ERROR_LOG_FILE = get_full_path("logs/error.log")

logs_full_path = get_full_path("logs")
if not os.path.exists(logs_full_path):
    os.mkdir(logs_full_path)


def _get_info_handler() -> logging.StreamHandler:
    """Вывод информационного сообщения в консоль"""
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(SHORT_FORMATTER)
    console_handler.setLevel(logging.INFO)
    return console_handler


def _get_info_handler_log() -> logging.FileHandler:
    """Запись информационного сообщения в файл"""
    file_handler = logging.FileHandler(filename=EVENT_LOG_FILE)
    file_handler.setFormatter(FORMATTER)
    file_handler.setLevel(logging.INFO)
    return file_handler


def _get_error_handler() -> logging.StreamHandler:
    """Вывод сообщения об ошибке в консоль"""
    console_handler = logging.StreamHandler(stream=sys.stderr)
    console_handler.setFormatter(SHORT_FORMATTER)
    console_handler.setLevel(logging.WARNING)
    return console_handler


def _get_error_handler_log() -> logging.FileHandler:
    """Запись сообщения об ошибке в файл"""
    file_handler = logging.FileHandler(filename=ERROR_LOG_FILE)
    file_handler.setFormatter(FORMATTER)
    file_handler.setLevel(logging.WARNING)
    return file_handler


def get_info_logger(logger_name: str) -> logging.Logger:
    """Создание логера для информационных сообщений"""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_get_info_handler())
    logger.addHandler(_get_info_handler_log())
    return logger


def get_error_logger(logger_name: str) -> logging.Logger:
    """Создание логера для ошибок"""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.WARNING)
    logger.addHandler(_get_error_handler())
    logger.addHandler(_get_error_handler_log())
    return logger
