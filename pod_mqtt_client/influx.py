from influxdb_client import InfluxDBClient, rest
from influxdb_client.client.write_api import ASYNCHRONOUS
from config import get_settings, json
from log import save_event
from datetime import datetime

connect = []


def connection_to_influx():
    # get setting for connect to influx
    org, token, url = get_settings("influx_settings")

    # connect to influx
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=ASYNCHRONOUS)

    global connect
    if client.health().status == "pass":
        connect = [org, write_api]
        print("Connection to InfluxDB: Successful")
    else:
        connect = None
        save_event(f"Connection to InfluxDB: Fail; Reason: {client.health().message}")

    return connect


def get_current_date() -> str:
    """Example: 2021-01-19T17:17:47.989506Z"""
    return datetime.utcnow().isoformat() + "Z"


def get_correct_timestamp(ts, current_date) -> str:
    """Get date from json or get current time"""
    date = current_date if ts is None else ts
    date_from_json = current_date if date[:4] == "1970" else date
    return str(date_from_json)


def get_bucket(name_bucket) -> str:
    """Get name "other" if influx table is not created"""
    return name_bucket if name_bucket in get_settings("used_bucket") else "other"


def convert_to_float(value):
    """Try to return float otherwise str"""
    try:
        return float(value)
    except ValueError:
        return value


def convert_to_json(value):
    """Try to return dict otherwise str"""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def unpacking_response(value) -> tuple:

    current_date = get_current_date()

    # Maybe float is here
    converted_value = convert_to_float(value)
    if isinstance(converted_value, float):
        return {"value": converted_value}, current_date

    # Maybe it's a json
    converted_value = convert_to_json(value)
    if isinstance(converted_value, dict):
        date_from_json = get_correct_timestamp(converted_value.get("timestamp"), current_date)

        if "value" in converted_value:
            value_from_json = converted_value.get("value")
        elif "val" in converted_value:
            value_from_json = converted_value.get("val")
        else:
            response = {k: convert_to_float(v) for k, v in converted_value.items() if k != "timestamp"}
            return response, date_from_json

        return {"value": convert_to_float(value_from_json)}, date_from_json

    # Most likely this is string
    return {"value": value}, current_date


def prepare_data(topic, value) -> list:
    """Create dictionary to write to influx"""
    records_list = []

    # Check topic and create dict
    topic_structure = topic.split("/")
    if len(topic_structure) == 3:
        template_tags = {}
    elif len(topic_structure) >= 5:
        template_tags = {"device": topic_structure[2].lower()}
    else:
        save_event(f"Unknown topic format: {topic}. Skip")
        return records_list

    bucket = get_bucket(topic_structure[1]).lower()  # database
    measurement = topic_structure[-1].lower()  # table

    # Read answer from broker
    unpacked_response = unpacking_response(value)
    values_dict, time_ = unpacked_response

    for key_, value_ in values_dict.items():
        if value_ is None:
            save_event(f"The value is none from topic: {topic}")
            continue
        elif isinstance(value_, float) and value_ in (-127.0, -128.0) and measurement in ("temp_out", "temp_in"):
            # (-127: controller lost sensor, -128: sensor is initializing)
            # save_event(f"Skip temp {value_} from topic: {topic}")
            continue

        tags = template_tags.copy()
        if key_ != "value":
            tags["type"] = key_

        new_record = {"bucket": bucket,
                      "measurement": measurement + "_info" if isinstance(value_, str) else measurement,
                      "time": str(time_),
                      "fields": {"value": value_},
                      "tags": tags}

        records_list.append(new_record)

    return records_list


def write_influx(topic, value):
    data_to_write = prepare_data(topic, value)

    if data_to_write:
        org, write_api = connect

        try:
            write_api.write(bucket=data_to_write[0].get("bucket"), org=org, record=data_to_write)
        except rest.ApiException:
            save_event(f"Can't record topic: {topic}; value: {value}")
