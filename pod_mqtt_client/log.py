from datetime import datetime
import config


def save_event(*args):
    """Save errors and other important messages to file"""

    if config.get_settings("EVENTLOG_ENABLE"):
        with open("event_log", "a") as log:
            print(datetime.now(), *args, file=log)
    else:
        print(datetime.now(), *args)
