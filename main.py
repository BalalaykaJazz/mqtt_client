#!/usr/bin/env python
from mqtt import connection_to_broker, start_mqtt, subscribe
from influx import connection_to_influx
from log import save_event
import config


def start():
    error_text = config.load_and_check_settings()
    if not error_text:
        print("Loading config: Successful")
    else:
        error_message = f"Loading config: Fail; Reason: {error_text}"
        print(error_message)
        save_event(error_message)
        return

    mqtt_connection = connection_to_broker()
    if mqtt_connection is None:
        return

    influx_connection = connection_to_influx()
    if influx_connection is None:
        return

    # FULL MODE
    subscribe([])

    # DEBUG MODE:
    # subscribe(["PZEM_CURRENT"])

    start_mqtt(mqtt_connection)


if __name__ == "__main__":
    start()
