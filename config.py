import json

mqtt_connection_status = {0: "Successful",
                          1: "Connection refused – incorrect protocol version",
                          2: "Connection refused – invalid client identifier",
                          3: "Connection refused – server unavailable",
                          4: "Connection refused – bad username or password",
                          5: "Connection refused – not authorised",
                          6: "Currently unused"}

value_types = {"sendmail": str, "alive": str, "sensor_baselog": str, "log": str, "info": str, "time_up": str,
               "temp_in": float, "temp_out": float,
               "b1": float, "b2": float,
               "sct013_1": float, "sct013_2": float, "sct013_3": float, "sct013x3": float,
               "rtdi1": float, "rtdi2": float, "rtdi3": float, "rtdi4": float, "rtdi5": float}

mqtt_settings = {}
influx_settings = {}
topics = {}  # Attention. If you add a new topic, do not forget to change prepare_data in influx.py


def load_settings():
    with open('settings.json', 'r', encoding='utf-8') as file2:

        settings = json.load(file2)
        global mqtt_settings
        mqtt_settings = settings.get("mqtt_settings")
        global influx_settings
        influx_settings = settings.get("influx_settings")
        global topics
        topics = settings.get("topics")


load_settings()
