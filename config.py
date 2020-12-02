import json
from collections import namedtuple

_settings = {}


def get_settings(name):
    return _settings.get(name)


def save_settings():
    """Save settings to json"""
    with open('settings.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(_settings.mqtt_connection_status, indent=4))


def check_settings():
    # settings shouldn't be empty
    for setting in _settings:
        if not setting:
            print("Settings are incorrect")
            return False

    return True


def from_dict_to_namedtuple(name, original_dict):
    return namedtuple(name, original_dict.keys())(*original_dict.values())


def load_and_check_settings():
    """Load from settings.json mqtt and influx settings, topics and value types"""
    with open("settings.json", encoding="utf-8") as file:

        settings = json.load(file)  # from
        global _settings  # to

        # mqtt_connection_status == tuple and other namedtuple
        _settings["mqtt_connection_status"] = tuple(settings.get("mqtt_connection_status"))
        _settings["mqtt_settings"] = from_dict_to_namedtuple("mqtt_settings", settings.get("mqtt_settings"))
        _settings["influx_settings"] = from_dict_to_namedtuple("influx_settings", settings.get("influx_settings"))
        _settings["topics"] = from_dict_to_namedtuple("topics", settings.get("topics"))

        value_types_dict = {x[0]: str if x[1] == "str" else float for x in settings.get("value_types").items()}
        _settings["value_types"] = from_dict_to_namedtuple("value_types", value_types_dict)

    return check_settings()
