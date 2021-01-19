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
    return datetime.utcnow().isoformat() + "Z"


def convert_value(type_value, value) -> tuple:
    try:  # try convert string to value type, example - float
        return type_value(value), get_current_date()
    except ValueError:
        try:  # try convert json to value type
            value_in_dict = json.loads(value)

            # check correct date
            year = value_in_dict.get("timestamp")[:4]
            date_from_json = get_current_date() if year == "1970" else value_in_dict.get("timestamp")

            return type_value(value_in_dict.get("value")), date_from_json
        except json.JSONDecodeError:
            return None, None


def get_type_value_from_name(value_types, type_name):
    return getattr(value_types, type_name)


def get_bucket(name_bucket) -> str:
    """get name "other" if influx table is not created"""
    return name_bucket if name_bucket in get_settings("used_bucket") else "other"


def prepare_data(topic, value) -> dict:
    """Get names fields to write to Influx"""
    result = topic.split("/")
    if len(result) == 3:
        prepared_data = {"measurement": result[1], "tags": {}}
    elif len(result) == 5:
        prepared_data = {"measurement": result[3], "tags": {"device": result[2]}}
    elif len(result) == 6:
        prepared_data = {"measurement": result[4], "tags": {"device": result[2]}}
    elif len(result) == 7:
        prepared_data = {"measurement": result[3], "tags": {"device": result[5]}}
    else:
        save_event(f"Unknown topic format: {topic}. Skip")
        return {}

    type_name = result[-1]
    prepared_data["tags"]["type"] = type_name
    prepared_data["bucket"] = get_bucket(result[1])

    # convert value (string) to required type
    type_value = get_type_value_from_name(get_settings("value_types"), type_name)
    converted_value = convert_value(type_value, value)

    if converted_value[0] is None:
        save_event(f"The value is none from topic: {topic}")
        return {}

    prepared_data["fields"] = {"value": converted_value[0]}
    prepared_data["time"] = str(converted_value[1])

    # select a table by type
    prepared_data["measurement"] += "_float" if type_value is float else "_str"
    return prepared_data


def write_influx(topic, value):
    data_to_write = prepare_data(topic, value)

    if data_to_write:
        org, write_api = connect
        write_api.write(bucket=data_to_write.get("bucket"), org=org, record=data_to_write)
