"""Модуль используется для записи в базу данных"""
from typing import Any, Optional
from datetime import datetime
from influxdb_client import InfluxDBClient, rest
from influxdb_client.client.write_api import ASYNCHRONOUS
from .config import get_setting, json
from .event_logger import get_info_logger, get_error_logger

event_log = get_info_logger("INFO_influx")
error_log = get_error_logger("ERR_influx")


class DatabaseConnectionError(Exception):
    """Исключение для ошибок при подключении к базе данных"""


class ErrorTopicFormat(Exception):
    """Исключение для ошибок в формате темы-источника сообщения"""


class Connect:
    """Подключение к базе данных"""

    def __init__(self):
        self.org = None
        self.write_api = None

    def create_connect(self, org, write_api):
        """Создание подключения"""
        self.org = org
        self.write_api = write_api

    def get_connect(self):
        """Возвращает параметры подключения"""
        return self.org, self.write_api


connect = Connect()


def connection_to_influx():
    """
    Создание подключения к базе данных.
    Результат подключения записывается в глобальную переменную connect.
    """

    # Settings
    org, token, url = get_setting("influx_settings")

    # Connection
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=ASYNCHRONOUS)

    if client.health().status == "pass":
        connect.create_connect(org=org, write_api=write_api)
        event_log.info("Успешное подключение к базе данных %s", url)
    else:
        error_log.error("Подключение к базе данных %s закончилось ошибкой %s",
                        url,
                        client.health().message)
        raise DatabaseConnectionError


def get_current_date() -> str:
    """
    Возвращает текущую дату и время в нужном формате.
    Пример: 2021-01-19T17:17:47.989506Z
    """

    return datetime.utcnow().isoformat() + "Z"


def get_correct_timestamp(timestamp: Optional[str], current_date: str) -> str:
    """
    Возвращает дату и время в строковом формате.
    Если дата не получена из сообщения (json), то возвращается текущая дата.
    """

    date = current_date\
        if (not timestamp or timestamp[:4] == "1970") \
        else timestamp

    return str(date)


def get_bucket(name_bucket: str) -> str:
    """
    Возвращает допустимое имя базы данных. Если предложенное имя не зарегистрировано
    в системе, то возвращается other.

    Это связано с тем, что перед записью данных база данных должна быть создана и настроена.
    """

    return name_bucket.lower()\
        if name_bucket in get_setting("used_bucket")\
        else "other"


def convert_to_float(value: str) -> Any:
    """
    Если получено числовое значение в строковом формате, то возвращается float,
    иначе возвращается строка.
    """

    try:
        return float(value)
    except ValueError:
        return value


def convert_to_json(value: str) -> Any:
    """
    Если получено сообщение в формате json, то возвращается словарь,
    иначе возвращается строка.
    """

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def unpacking_response(value: str) -> tuple:
    """
    Возвращает кортеж из полученного значения и даты для записи.
    Если входящее сообщение имеет формат json, то в нем может быть указана дата события,
    поэтому дата и значение обрабатываются одновременно.
    """

    current_date = get_current_date()

    # Если полученное значение является числом, то дата для записи - текущая дата.
    converted_value = convert_to_float(value)
    if isinstance(converted_value, float):
        return {"value": converted_value}, current_date

    # Если полученное значение имеет формат json, то берем дату для записи оттуда.
    # Если дата не указана, то используем текущую дату.
    converted_value = convert_to_json(value)
    if isinstance(converted_value, dict):
        date_from_json = get_correct_timestamp(converted_value.get("timestamp"), current_date)

        if "value" in converted_value:
            value_from_json = converted_value["value"]
        elif "val" in converted_value:
            value_from_json = converted_value["val"]
        else:
            response = {k: convert_to_float(v)
                        for k, v in converted_value.items()
                        if k != "timestamp"}
            return {"value": response}, date_from_json

        return {"value": convert_to_float(value_from_json)}, date_from_json

    # Полученное значение записывается как строка
    return {"value": value}, current_date


def get_device_section(topic_structure: list) -> dict:
    """Возвращает словарь с секцией device для записи в БД"""

    if len(topic_structure) == 3:
        tags_section = {}
    elif len(topic_structure) >= 5:
        tags_section = {"device": topic_structure[2].lower()}
    else:
        raise ErrorTopicFormat

    return tags_section


def skip_record(value: Any, measurement: str, topic: str) -> bool:
    """Пропускает ненужные записи."""

    if value is None:
        error_log.error("Полученное сообщение имеет некорректный формат. Отправитель: %s",
                        topic)
        return True

    if isinstance(value, float) \
            and value in (-127.0, -128.0) \
            and measurement in ("temp_out", "temp_in"):
        # (-127: controller lost sensor, -128: sensor is initializing)
        return True

    return False


def prepare_data(topic: str, value: str) -> list:
    """Возвращает список словарей для записи в базу данных."""

    records_list: list = []

    # Check topic and create dict
    topic_structure = topic.split("/")

    try:
        device_section = get_device_section(topic_structure)
    except ErrorTopicFormat:
        error_log.error("Неизвестный формат темы %s. Сообщение пропущено.", topic)
        return records_list

    # Read answer from broker
    values_dict, timestamp = unpacking_response(value)

    measurement = topic_structure[-1].lower()  # table name
    bucket_section = get_bucket(topic_structure[1])  # database name
    time_section = str(timestamp)

    for key_, value_ in values_dict.items():
        if skip_record(value_, measurement, topic):
            continue

        measurement_section = measurement + "_info" if isinstance(value_, str) else measurement
        tags = device_section.copy()
        if key_ != "value":
            tags["type"] = key_

        new_record = {"bucket": bucket_section,
                      "measurement": measurement_section,
                      "time": time_section,
                      "fields": {"value": value_},
                      "tags": tags}

        records_list.append(new_record)

    return records_list


def write_to_database(topic: str, value: str):
    """
    Запись в базу данных.
    topic: str - источник сообщения, value: str - сообщение в строковом формате.
    Текстовое сообщение преобразуется в список словарей в функции prepare_data().
    Если не удалось записать сообщение, то делаем запись в журнале и продолжаем штатную работу.
    """

    data_to_write = prepare_data(topic, value)

    if data_to_write:
        org, write_api = connect.get_connect()

        try:
            write_api.write(bucket=data_to_write[0].get("bucket"),
                            org=org,
                            record=data_to_write)
        except rest.ApiException:
            error_log.error("Ошибка при записи данных. Топик %s, значение %s", topic, value)
