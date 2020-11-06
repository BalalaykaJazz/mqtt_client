import paho.mqtt.client as mqtt
from config import mqtt_settings, mqtt_connection_status, topics
from influx import write_influx


def connection_to_broker():
    # Settings
    print(mqtt_settings)
    print(type(mqtt_settings))
    broker_url = mqtt_settings.get("broker_url")
    broker_port = mqtt_settings.get("broker_port")
    mqtt_login = mqtt_settings.get("mqtt_login")
    mqtt_pass = mqtt_settings.get("mqtt_pass")

    # Connection
    _client = mqtt.Client()
    _client.on_connect = on_connect
    _client.on_disconnect = on_disconnect
    _client.on_message = on_message
    _client.username_pw_set(username=mqtt_login, password=mqtt_pass)
    _client.connect(broker_url, broker_port)

    return _client


def subscribe_to_topic(_client, topic, qos=1):  # qos = 1 - At Least Once
    _client.subscribe(topic, qos=qos)


def subscribe_to_all(_client, qos=1):
    for value in topics.values():
        subscribe_to_topic(_client, value, qos)


def on_connect(_client, userdata, flags, rc):
    label = mqtt_connection_status.get(rc) if rc in range(0, 6) else "Currently unused"
    print(f"Connection to broker: {label}")
    subscribe_to_all(_client)


def on_disconnect(_client, userdata, rc):
    print("Client Got Disconnected")


def on_message(_client, userdata, message):
    try:
        value = message.payload.decode()
    except UnicodeDecodeError:
        return

    print(f"Message received. Topic: {message.topic}, value: {value}")
    write_influx(message.topic, message.payload.decode())


def start_mqtt(client):
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Client Got Disconnected")
