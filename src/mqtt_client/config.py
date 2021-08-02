"""
Модуль используется для считывания файлов, необходимых для корректной работы сервиса.
"""
import json
import os.path
from collections import namedtuple
from typing import Any
from pydantic import BaseSettings
from .event_logger import get_info_logger, get_error_logger
from .common_func import get_full_path


TOPICS_PATH = "settings/topics.json"
MQTT_CONNECTION_STATUS = [
    "Successful",
    "Connection refused \u2013 incorrect protocol version",
    "Connection refused \u2013 invalid client identifier",
    "Connection refused \u2013 server unavailable",
    "Connection refused \u2013 bad username or password",
    "Connection refused \u2013 not authorised",
    "Currently unused"]

event_log = get_info_logger("INFO_config")
error_log = get_error_logger("ERR_config")


class SettingsError(Exception):
    """Исключение для ошибок в конфигурационном файле."""


class Settings(BaseSettings):  # pylint: disable = too-few-public-methods
    """
    Параметры подключения к внешним ресурсам.

    mqtt_settings - подключение к брокеру mqtt для получения сообщий от устройств.
    - ca_certs, certfile, keyfile - путь к сертификатам для работы tls.

    database_settings - подключение к базе данных для записи сообщений.
    - org - Организация в базе данных.
    - token - токен для доступа к БД или связка login:password.
    - url - адрес базы данных.

    - version - текущая версия файла настроек.
    - is_eventlog_enable - Режим записи событий в лог. Если выключено,
    то выводится только в консоль.
    - is_debug_mode - Режим отладки. Если включен, то программа подписывается
    только на указанные в debug_subscribe топики.
    - debug_subscribe - Список топиков для режима отладки.
    - used_bucket - таблицы, которые используются в базе данных.
    """

    # mqtt_settings
    broker_url: str = ""
    broker_port: int = 8883
    mqtt_login: str = ""
    mqtt_pass: str = ""
    ca_certs: str = ""
    certfile: str = ""
    keyfile: str = ""
    tls: dict = {}
    mqtt_connection_status = MQTT_CONNECTION_STATUS

    # database_settings
    org: str = ""
    token: str = ""
    url: str = ""

    # settings
    version: str = ""
    is_eventlog_enable: bool = True
    is_debug_mode: bool = False
    debug_subscribe: list = []
    used_bucket: list = []
    topics: dict = {}


def from_dict_to_namedtuple(name_dict, original_dict) -> tuple[str]:
    """Конвертирует настройки из словаря в namedtuple"""

    return namedtuple(name_dict, original_dict.keys())(*original_dict.values())


def read_file(file_name: str) -> dict[str, str]:
    """
    Функция читает указанный в file_name файл и возвращает словарь с полученными полями.
    """

    try:
        with open(get_full_path(file_name), encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as err:
        error_log.error("Не найден файл %s", file_name)
        raise SettingsError from err
    except json.decoder.JSONDecodeError as err:
        error_log.error("Файл %s имеет некорректный формат.", file_name)
        raise SettingsError from err


def load_topics():
    """Загрузка топиков к которым можно подписаться в брокере mqtt."""

    try:
        loaded_settings = read_file(TOPICS_PATH)
        settings.topics = from_dict_to_namedtuple("topics", loaded_settings)
    except (SettingsError, KeyError):
        error_log.error("Ошибка загрузки конфигурационного файла: %s", TOPICS_PATH)
        raise SettingsError  # pylint: disable = raise-missing-from


def check_settings():
    """
    Проверка загруженных настроек перед дальнейшим использованием.
    """

    correct_mqtt_settings = ("broker_url", "broker_port", "mqtt_login", "mqtt_pass")
    for current_setting in correct_mqtt_settings:
        if not getattr(settings, current_setting):
            error_log.error("Не указано поле %s в настройке брокера mqtt", current_setting)
            raise SettingsError

    correct_tls = (settings.ca_certs, settings.certfile, settings.keyfile)
    for tls_file_name in correct_tls:
        if not os.path.exists(get_full_path(tls_file_name)):
            error_log.error("Не найден файл %s требуемый для подключения к брокеру mqtt",
                            tls_file_name)
            raise SettingsError

    correct_db_settings = ("org", "token", "url")
    for current_setting in correct_db_settings:
        if not getattr(settings, current_setting):
            error_log.error("Не указано поле %s в настройке базы данных", current_setting)
            raise SettingsError

    if not settings.topics:
        error_log.error("Не обнаружены топики для подписки. Заполните файл topics.json")
        raise SettingsError


def get_setting(setting_name: str) -> Any:
    """Возвращает запрошенные в параметре setting_name настройки."""

    if setting_name == "mqtt_settings":
        return settings.broker_url, settings.broker_port,\
               settings.mqtt_login, settings.mqtt_pass,\
               settings.tls

    if setting_name == "influx_settings":
        return settings.org, settings.token, settings.url

    return getattr(settings, setting_name)


def get_topic(topic_name: str) -> Any:
    """Возвращает запрошенный в topic_name топик"""

    return getattr(settings.topics, topic_name)


settings = Settings(_env_file=get_full_path(".env"),
                    _env_file_encoding="utf-8")
settings.tls = {"ca_certs": settings.ca_certs,
                "certfile": settings.certfile,
                "keyfile": settings.keyfile}

load_topics()
