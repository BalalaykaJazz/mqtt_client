#!/usr/bin/env python
from mqtt import connection_to_broker, subscribe_to_topic, start_mqtt
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
    # for testing:
    # subscribe_to_topic(client, config.get_settings("topics").MOXA_rtdi0)
    # subscribe_to_topic(client, config.get_settings("topics").MOXA_rtdi1)
    # subscribe_to_topic(client, config.get_settings("topics").MOXA_rtdi2)
    # subscribe_to_topic(client, config.get_settings("topics").MOXA_rtdi3)
    # subscribe_to_topic(client, config.get_settings("topics").MOXA_rtdi4)
    # subscribe_to_topic(client, config.get_settings("topics").MOXA_rtdi5)
    start_mqtt(client)


if __name__ == "__main__":
    start()
