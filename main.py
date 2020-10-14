from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from collections import namedtuple


def get_settings_influx():

    # bucket - influx base name
    # url - influx source
    # org & token - optional values
    return namedtuple("settings", "bucket org token url")("sensor", "NA", "none", "http://localhost:8086")


def connect_to_influx():

    # get setting for connect to influx
    bucket, org, token, url = get_settings_influx()

    # connect to influx
    client = InfluxDBClient(url=url, token=token, org=org)
    return namedtuple("connect", "bucket org client")(bucket, org, client)


def create_record(field_value, table_name="temperature", tag_name="location", tag_value="room1", field_name="internal"):

    return Point(table_name).tag(tag_name, tag_value).field(field_name, field_value)


def get_records(data=None):

    record_list = []

    if data is None:  # get data from user

        while True:
            try:
                user_input = input("Press enter a number or text 'exit': ")

                if user_input == "exit":
                    break
                else:
                    field_value = float(user_input)

            except ValueError:
                print("This is not a number. Skip")
                continue

            result = create_record(field_value)
            record_list.append(result)

    # else:  # prepare data from mqtt
    # coming soon
    #     for rec in data:
    #         result = create_record(rec)
    #
    #         if result:
    #             record_list.append(result)

    return record_list


def report_to_user(count):
    print(f"Written {count} lines")


def write_influx():

    # Connect to influx
    bucket, org, client = connect_to_influx()

    write_api = client.write_api(write_options=SYNCHRONOUS)

    record_list = get_records()

    if record_list:
        write_api.write(bucket=bucket, org=org, record=record_list)

    report_to_user(len(record_list))


write_influx()

# influx -precision rfc3339
# select * from temperature
