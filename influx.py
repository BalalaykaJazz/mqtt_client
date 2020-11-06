from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import influx_settings, value_types, json

connect = []


def connection_to_influx():
    # get setting for connect to influx
    bucket = influx_settings.get("bucket")
    org = influx_settings.get("org")
    token = influx_settings.get("token")
    url = influx_settings.get("url")

    # connect to influx
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    print(f"Connection to InfluxDB: Successful")

    global connect
    connect = [bucket, org, write_api]
    return connect


def create_record(field_value, table_name="unknown", device_name="unknown", type_name="unknown"):
    return Point(table_name).tag("device", device_name).tag("type", type_name).field("value", field_value)


def convert_value(type_value, value):

    try:
        return type_value(value)  # convert string to type, example - float
    except ValueError:
        try:
            d = json.loads(value)  # dict
            value_string = d.get("value")  # string
            return convert_value(type_value, value_string)
        except json.JSONDecodeError:
            return None


def prepare_data(topic, value):
    # get names to write to Influx
    result = topic.split("/")
    if len(result) == 5:
        kwargs = {"table_name": result[3], "device_name": result[2], "type_name": result[-1]}
    elif len(result) == 3:
        kwargs = {"table_name": result[1], "type_name": result[-1]}
    elif len(result) == 6:
        kwargs = {"table_name": result[4], "device_name": result[2], "type_name": result[-1]}
    elif len(result) == 7:
        kwargs = {"table_name": result[3], "device_name": result[5], "type_name": result[-1]}
    else:
        return create_record(field_value=value)

    # convert value to required type
    type_value = value_types[kwargs["type_name"]]
    converted_value = convert_value(type_value, value)

    if converted_value is None:
        return create_record(field_value=value)
    else:
        kwargs["field_value"] = converted_value

    # select a table by type
    kwargs["table_name"] = kwargs["table_name"] + "_float" if type_value is float else "_str"
    return create_record(**kwargs)


def write_influx(topic, value):
    bucket, org, write_api = connect
    write_api.write(bucket=bucket, org=org, record=prepare_data(topic, value))
