#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Модуль используется для запуска сервиса клиента mqtt.
"""
from time import sleep
from src.mqtt_client.mqtt import connection_to_broker, start_mqtt
from src.mqtt_client.common_func import ClientError, BrokerConnectionError
from src.mqtt_client.database import connection_to_db, DatabaseConnectionError
import src.mqtt_client.config as config
from src.mqtt_client.event_logger import get_info_logger, get_error_logger

RESTART_TIMEOUT = 60
event_log = get_info_logger("INFO_mqtt_client_run")
error_log = get_error_logger("ERR_mqtt_client_run")


def restart_client(message: str):
    """Перезапуск клиента после паузы с выводом сообщения."""

    error_log.warning("Перезапуск сервиса по причине: %s", message)
    sleep(RESTART_TIMEOUT)
    start_client()


def start_client():
    """
    Подключение к брокеру mqtt и базе данных. При невозможности подключения
    отправляется сообщение в stderr и производится повторное подключение через ERROR_TIMEOUT.
    """

    try:
        mqtt_connection = connection_to_broker()
    except BrokerConnectionError:
        restart_client("Ошибка при подключении к брокеру mqtt")
        return

    try:
        connection_to_db()
    except DatabaseConnectionError:
        restart_client("Ошибка при подключении к базе данных")
        return

    try:
        start_mqtt(mqtt_connection)
    except ClientError:
        restart_client("Ошибка при работе клиента")
        return


if __name__ == "__main__":
    try:
        config.check_settings()
    except config.SettingsError:
        error_log.error("Ошибка при загрузке настроек.")
        raise SystemExit("Работа программы завершена.")  # pylint: disable = raise-missing-from

    event_log.info("Старт работы клиента")
    start_client()
