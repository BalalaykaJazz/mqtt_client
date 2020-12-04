#!/usr/bin/env python
from mqtt import connection_to_broker, start_mqtt, subscribe
from influx import connection_to_influx
import config


def start():
    if config.load_and_check_settings():
        print("Loading settings: Successful")
    else:
        print("Execution completed")
        return

    client = connection_to_broker()
    connection_to_influx()

    # FULL MODE
    subscribe([])

    # DEBUG MODE:
    # subscribe(["MOXA_rtdi0", "MOXA_rtdi1", "MOXA_rtdi2", "MOXA_rtdi3", "MOXA_rtdi4", "MOXA_rtdi5"])

    start_mqtt(client)


if __name__ == "__main__":
    start()
