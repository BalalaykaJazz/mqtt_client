import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from collections import namedtuple


def get_settings_influx():
    # bucket - influx BD name
    # url - influx source
    return namedtuple("settings", "bucket org token url")("sensor", "NA", "none", "http://localhost:8086")


def get_date_to_record():
    try:
        temp = float(input("Press enter a number: "))
    except ValueError:
        print("This is not a number")
        return None

    return namedtuple("record",
                      "table_name tag_name tag_value field_name field_value") \
        ("temperature", "location", "room1", "internal", temp)


def write_influx():
    # Manual: INSERT temperature4,type=sensor1 internal=37

    # get setting to connect influx
    bucket, org, token, url = get_settings_influx()

    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    date = get_date_to_record()

    if date:
        p = influxdb_client.Point(date.table_name).tag(date.tag_name, date.tag_value).field(date.field_name,
                                                                                            date.field_value)
        write_api.write(bucket=bucket, org=org, record=p)


write_influx()
