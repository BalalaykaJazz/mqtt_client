#!/usr/bin/env python
from mqtt import connection_to_broker, subscribe_to_topic, start_mqtt
from influx import connection_to_influx
from config import topics

if __name__ == "__main__":
    client = connection_to_broker()
    connection_to_influx()
    # for testing:
    # subscribe_to_topic(client, topics["MOXA_rtdi1"])
    start_mqtt(client)
