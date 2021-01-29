from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from config import get_settings, json
from log import save_event
from datetime import datetime

connect = []


def connection_to_influx():
    # get setting for connect to influx
    influx_settings = get_settings("influx_settings")
    org = influx_settings.org
    token = influx_settings.token
    url = influx_settings.url

    # connect to influx
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    global connect
    if client.health().status == "pass":
        connect = [org, write_api]
        print("Connection to InfluxDB: Successful")
    else:
        connect = None
        error_message = f"Connection to InfluxDB: Fail; Reason: {client.health().message}"
        print(error_message)
        save_event(error_message)

    return connect


def get_current_date() -> str:
    """Example: 2021-01-19T17:17:47.989506Z"""
    return datetime.utcnow().isoformat() + "Z"


def convert_value(value) -> tuple:
    try:  # maybe float is here
        return float(value), get_current_date()
    except ValueError:
        pass

    try:  # Maybe it's a json
        value_in_dict = json.loads(value)

        # get value from json
        if "value" in value_in_dict:
            value_from_json = value_in_dict.get("value")
        elif "val" in value_in_dict:
            value_from_json = value_in_dict.get("val")
        else:
            return None, None  # incorrect json

        # get date from json or get current time
        date = get_current_date() if value_in_dict.get("timestamp") is None else value_in_dict.get("timestamp")
        date_from_json = get_current_date() if date[:4] == "1970" else date

        return float(value_from_json), date_from_json
    except json.JSONDecodeError:
        pass

    return value, get_current_date()  # normal string


def get_bucket(name_bucket) -> str:
    """get name "other" if influx table is not created"""
    return name_bucket if name_bucket in get_settings("used_bucket") else "other"


def prepare_data(topic, value) -> dict:
    """Get names fields to write to Influx"""
    result = topic.split("/")
    if len(result) == 3:
        prepared_data = {"tags": {}}
    elif len(result) >= 5:
        prepared_data = {"tags": {"device": result[2].lower()}}
    else:
        save_event(f"Unknown topic format: {topic}. Skip")
        return {}

    prepared_data["bucket"] = get_bucket(result[1]).lower()  # database
    prepared_data["measurement"] = result[-1].lower()  # table

    unpacked_response = convert_value(value)  # pair converted value and time
    converted_value = unpacked_response[0]

    if converted_value is None:
        save_event(f"The value is none from topic: {topic}")
        return {}
    elif converted_value is float and int(converted_value) in (-127, -128) \
            and prepared_data["measurement"] in ("temp_out", "temp_in"):
        # (-127: controller lost sensor, -128: sensor is initializing)
        save_event(f"Skip temp {converted_value} from topic: {topic}")
        return {}

    prepared_data["fields"] = {"value": converted_value}
    prepared_data["time"] = str(unpacked_response[1])

    return prepared_data


def write_influx(topic, value):
    data_to_write = prepare_data(topic, value)

    if data_to_write:
        org, write_api = connect
        write_api.write(bucket=data_to_write.get("bucket"), org=org, record=data_to_write)
