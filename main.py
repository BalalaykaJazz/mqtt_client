from mqtt import connection_to_broker, subscribe_to_topic, subscribe_to_all, start_mqtt
from influx import connection_to_influx
from config import *

if __name__ == "__main__":

    # mqtt
    client = connection_to_broker()
    # for testing:
    # subscribe_to_topic(client, topics["TEMP_OUT"])

    # influxDB
    connection_to_influx()

    start_mqtt(client)

# manual for InfluxDB:
# influx -precision rfc3339
# use sensor
# select * from temperature
# INSERT temperature,machine=unit42,type=assembly external=25,internal=37
# DELETE FROM "temperature"
# sudo du -sh /var/lib/influxdb/data/<db name> # base size
# https://mntolia.com/mqtt-python-with-paho-mqtt-client/#41_The_Loop_Functions
