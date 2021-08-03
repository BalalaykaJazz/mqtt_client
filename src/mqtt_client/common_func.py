"""Общие функции"""
import os


def get_full_path(file_name: str) -> str:
    """Возвращает полный путь к файлу."""

    return os.path.join(os.path.dirname(__file__), file_name)


class ClientError(Exception):
    """Исключение для ошибок при работе клиента"""


class BrokerConnectionError(Exception):
    """Исключение для ошибок при подключении к брокеру"""


class SettingsError(Exception):
    """Исключение для ошибок в конфигурационном файле."""


class DatabaseConnectionError(Exception):
    """Исключение для ошибок при подключении к базе данных"""


class ErrorTopicFormat(Exception):
    """Исключение для ошибок в формате темы-источника сообщения"""
