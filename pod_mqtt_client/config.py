import json
import os.path
from collections import namedtuple
from log import save_event

settings_full_path = os.path.join(os.path.dirname(__file__), 'settings/settings.json')
_settings = {}


def get_settings(name):
    return _settings.get(name)


def get_topic(name):
    return getattr(get_settings("topics"), name)


def save_settings():
    """Save settings to json"""
    with open(settings_full_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(_settings["mqtt_connection_status"], indent=4))


def check_settings(settings) -> str:
    """If something is wrong, we will return error description"""

    # settings must contain required fields
    correct_settings = ("General", "mqtt_connection_status", "mqtt_settings", "influx_settings", "topics", "used_bucket")
    for current_setting in correct_settings:
        if current_setting not in settings:
            return f"Settings don't contain field {current_setting}"

    correct_general = ("EVENTLOG_ENABLE", "DEBUG_MODE", "debug_subscribe")
    _general_settings = settings["General"]
    for current_setting in correct_general:
        if current_setting not in _general_settings:
            return f"General settings don't contain field {current_setting}"

    correct_mqtt_settings = ("broker_url", "broker_port", "mqtt_login", "mqtt_pass")
    _mqtt_settings = settings["mqtt_settings"]
    for current_setting in correct_mqtt_settings:
        if _mqtt_settings.get(current_setting) is None:
            return f"Mqtt_settings don't contain field {current_setting}"

    correct_influx_settings = ("org", "token", "url")
    _influx_settings = settings["influx_settings"]
    for current_setting in correct_influx_settings:
        if _influx_settings.get(current_setting) is None:
            return f"Influx_settings don't contain field {current_setting}"

    return ""


def from_dict_to_namedtuple(name, original_dict):
    return namedtuple(name, original_dict.keys())(*original_dict.values())


def load_and_check_settings() -> bool:
    """Load from settings.json mqtt and influx settings, topics and value types. Checking them"""

    no_error = False
    first_part_error = "Loading config: Fail; Reason:"

    try:
        with open(settings_full_path, encoding="utf-8") as file:

            settings = json.load(file)  # from
            global _settings  # to

            error_text = check_settings(settings)

            if error_text == "":
                # mqtt_connection_status and used_bucket == tuple and other namedtuple
                _settings["mqtt_connection_status"] = tuple(settings.get("mqtt_connection_status"))
                _settings["mqtt_settings"] = from_dict_to_namedtuple("mqtt_settings", settings.get("mqtt_settings"))
                _settings["influx_settings"] = from_dict_to_namedtuple("influx_settings",
                                                                       settings.get("influx_settings"))
                _settings["topics"] = from_dict_to_namedtuple("topics", settings.get("topics"))
                _settings["used_bucket"] = tuple(settings.get("used_bucket"))

                _settings.update(settings.get("General"))

                print("Loading config: Successful")
                no_error = True

            else:
                save_event(f"{first_part_error} {error_text}")

    except FileNotFoundError:
        save_event(f"{first_part_error} not found settings.json")
    except json.decoder.JSONDecodeError:
        save_event(f"{first_part_error} invalid file settings.json")

    return no_error
