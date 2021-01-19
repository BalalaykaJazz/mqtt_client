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

    # FULL MODE: subscribe to all known topics. Without notifications
    subscribe([])

    # OR

    # DEBUG MODE: subscribe to selected topics. Notification for each topic
    subscribe(["SENSOR_SCT_3ph"])
    # subscribe(["MOXA_rtdi1"])
    # subscribe(["MOXA_rtdi2"])
    # subscribe(["MOXA_rtdi3"])
    # subscribe(["MOXA_rtdi4"])
    # subscribe(["MOXA_rtdi5"])

    start_mqtt(mqtt_connection)


if __name__ == "__main__":
    start()
