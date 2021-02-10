#!/usr/bin/env python
from mqtt import connection_to_broker, start_mqtt, subscribe
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

    if config.get_settings("DEBUG_MODE"):  # Subscribe to selected topics. Notification for each topic
        subscribe(["MOXA_rtdi0"])
    else:  # FULL MODE: subscribe to all known topics. Without notifications
        subscribe([])

    start_mqtt(mqtt_connection)


if __name__ == "__main__":
    start()
