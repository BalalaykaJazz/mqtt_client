"""Модуль используется для получения сообщений от брокера mqtt"""
from typing import Any
import paho.mqtt.client as mqtt
from .config import get_setting, get_topic
from .database import write_to_database
from .event_logger import get_info_logger, get_error_logger
from .common_func import get_full_path, ClientError, BrokerConnectionError

event_log = get_info_logger("INFO_mqtt")
error_log = get_error_logger("ERR_mqtt")


def connection_to_broker() -> mqtt.Client:
    """Подключение к брокеру mqtt"""

    # Settings
    broker_url, broker_port, mqtt_login, mqtt_pass, tls_settings = get_setting("mqtt_settings")

    # Connection
    _client = mqtt.Client()
    _client.on_connect = on_connect
    _client.on_disconnect = on_disconnect
    _client.on_message = on_message
    _client.username_pw_set(username=mqtt_login, password=mqtt_pass)

    if tls_settings:  # if TLS is used
        _client.tls_set(ca_certs=get_full_path(tls_settings.get("ca_certs")),
                        certfile=get_full_path(tls_settings.get("certfile")),
                        keyfile=get_full_path(tls_settings.get("keyfile")))

    try:
        _client.connect(broker_url, broker_port, keepalive=10)
        event_log.info("Подключение к брокеру mqtt %s: Успешно", broker_url)
        return _client
    except Exception as err:
        error_log.error("Ошибка при подключении к брокеру mqtt: %s", str(err))
        raise BrokerConnectionError  # pylint: disable = raise-missing-from


def subscribe_to_topic(_client: mqtt.Client, topic: str, qos: int = 1):
    """Подписка на топик. Qos по умолчанию равен 1 (At Least Once)."""

    _client.subscribe(topic, qos=qos)


def subscribe_to_all(_client: mqtt.Client, qos: int = 1):
    """Подписка на все сущствующие топики, описанные в файле настройке topics"""

    for value in get_setting("topics"):
        subscribe_to_topic(_client, value, qos)


def on_connect(_client: Any, _, __, result_code: Any):
    """
    Обратный вызов, который вызывается каждый раз когда клиент
    подключается/переподключается к брокеру.
    """

    label = get_setting("mqtt_connection_status")[result_code]\
        if result_code in range(0, 6)\
        else "Currently unused"
    event_log.info("Статус подключения к mqtt %s", label)

    if get_setting("is_debug_mode"):
        # Подключение к выбранным топикам для отладки
        debug_subscribe_message = "Режим отладки включен для топиков: " +\
                                  ", ".join(get_setting("debug_subscribe"))
        event_log.info(debug_subscribe_message)
        for topic in get_setting("debug_subscribe"):
            subscribe_to_topic(_client, get_topic(topic))
    else:
        # Подключение ко всем доступным топикам
        subscribe_to_all(_client)


def on_disconnect(_client: Any, *_):
    """Событие при завершении соединения с брокером"""

    if get_setting("is_debug_mode"):
        event_log.info("Завершение соединения с брокером mqtt")


def on_message(_client: Any, _, message: Any):
    """
    Событие при получении сообщения. Сообщения с типом retain пропускаются.
    Успешно полученное и декодированное сообщение записывается в базу данных.
    """

    if message.retain == 1:
        return

    try:
        value = message.payload.decode()
    except UnicodeDecodeError:
        if get_setting("is_debug_mode"):
            error_log.warning("Не удалось декодировать сообщение для топика %s", message.topic)
        return

    if get_setting("is_debug_mode"):
        event_log.info("Получено сообщение. Topic: %s, value: %s", message.topic, value)

    # Запись сообщения в базу данных
    write_to_database(message.topic, value)


def start_mqtt(client: mqtt.Client):
    """Начало обработки сетевого трафика между клиентом и брокером."""

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        if get_setting("is_debug_mode"):
            event_log.info("Завершение соединения с брокером mqtt")
    except Exception as err:
        error_log.error("start_mqtt error: %s", str(err))
        raise ClientError  # pylint: disable = raise-missing-from
