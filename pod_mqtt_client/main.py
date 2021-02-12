#!/usr/bin/env python
from mqtt import connection_to_broker, start_mqtt
from influx import connection_to_influx
import config


def start():
    if not config.load_and_check_settings():
        return

    mqtt_connection = connection_to_broker()
    if mqtt_connection is None:
        return

    influx_connection = connection_to_influx()
    if influx_connection is None:
        return

    start_mqtt(mqtt_connection)


if __name__ == "__main__":
    start()
