#!/usr/bin/env python
from mqtt import connection_to_broker, start_mqtt, subscribe
from influx import connection_to_influx
import config


def start():
    if config.load_and_check_settings() is None:
        return

    mqtt_connection = connection_to_broker()
    if mqtt_connection is None:
        return

    influx_connection = connection_to_influx()
    if influx_connection is None:
        return

    # FULL MODE
    subscribe([])

    # OR

    # DEBUG MODE:
    # subscribe(["MOXA_rtdi0"])
    # subscribe(["MOXA_rtdi1"])
    # subscribe(["MOXA_rtdi2"])
    # subscribe(["MOXA_rtdi3"])
    # subscribe(["MOXA_rtdi4"])
    # subscribe(["MOXA_rtdi5"])

    start_mqtt(mqtt_connection)


if __name__ == "__main__":
    start()

    # from datetime import datetime
    # print(type(datetime.utcnow().isoformat() + "Z"))
    #
    # from influxdb_client import InfluxDBClient, Point
    # from influxdb_client.client.write_api import SYNCHRONOUS
    #
    # _client = InfluxDBClient(url="http://localhost:8086", token="none", org="NA")
    # _write_client = _client.write_api(write_options=SYNCHRONOUS)



    # p = Point("out_float_new10").tag("device", "e1260").tag("type", "rtdi5").field("value", 3276.8)
    # _write_client.write(bucket="sensor", org="NA", record=p)
    # _write_client.write("sensor", "NA",  {'measurement': 'out_float_new', 'tags': {'device': 'e1260', 'type': "rtdi5"},
    #                                       'fields': {"value": 3276.9}, 'time': d})
