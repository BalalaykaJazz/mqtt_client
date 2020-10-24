from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import influx_settings, value_types

connect = []


def connection_to_influx():

    # get setting for connect to influx
    bucket, org, token, url = influx_settings

    # connect to influx
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    print(f"Connection to InfluxDB: Successful")

    global connect
    connect = [bucket, org, write_api]
    return connect


def get_date_from_mqtt(topic, value):
    write_influx(topic, value)


def create_record(field_value, table_name="unknown", device_name="unknown", type_name="unknown"):

    return Point(table_name).tag("device", device_name).tag("type", type_name).field("value", field_value)


def prepare_data(topic, value):

    result = topic.split("/")
    if len(result) == 5:
        kwargs = {"table_name": result[3], "device_name": result[2], "type_name": result[4]}
    elif len(result) == 3:
        kwargs = {"table_name": result[1], "type_name": result[2]}
    elif len(result) == 6:
        kwargs = {"table_name": result[4], "device_name": result[2], "type_name": result[5]}
    else:
        return create_record(field_value=value)

    # convert value to required type
    type_value = value_types[kwargs["type_name"]]
    kwargs["field_value"] = type_value(value)

    # select a table by type
    kwargs["table_name"] = kwargs["table_name"] + "_float" if type_value is float else "_str"
    return create_record(**kwargs)


def write_influx(topic, value):

    bucket, org, write_api = connect
    write_api.write(bucket=bucket, org=org, record=prepare_data(topic, value))
