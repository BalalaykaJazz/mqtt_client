import json
from collections import namedtuple

_settings = {}


def get_settings(name):
    return _settings.get(name)


def get_topic(name):
    return getattr(get_settings("topics"), name)


def save_settings():
    """Save settings to json"""
    with open('settings.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(_settings.mqtt_connection_status, indent=4))


def check_settings():
    # settings shouldn't be empty
    if not _settings:
        return "Settings is empty"

    # settings must contain required fields
    correct_settings = ("mqtt_connection_status", "mqtt_settings", "influx_settings", "topics", "value_types")
    for setting in correct_settings:
        if setting not in _settings:
            return f"Settings don't contain filed {setting}"

    correct_mqtt_settings = ("broker_url", "broker_port", "mqtt_login", "mqtt_pass")
    _mqtt_settings = _settings["mqtt_settings"]
    for setting in correct_mqtt_settings:
        try:
            getattr(_mqtt_settings, setting)
        except AttributeError:
            return f"Mqtt_settings don't contain filed {setting}"

    correct_influx_settings = ("bucket", "org", "token", "url")
    _influx_settings = _settings["influx_settings"]
    for setting in correct_influx_settings:
        try:
            getattr(_influx_settings, setting)
        except AttributeError:
            return f"Influx_settings don't contain filed {setting}"

    # a value must be specified for each topic
    names_value_types = _settings["value_types"]._fields
    for topic in _settings["topics"]:
        type_name = topic.split("/")[-1]

        if type_name not in names_value_types:
            return f"Value_types don't contain filed {type_name}"

    return ""


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
