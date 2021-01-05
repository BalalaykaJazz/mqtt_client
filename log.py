from datetime import datetime


def save_event(*args, **kwargs):
    """Save errors and other important messages to file"""
    with open("event_log", "a") as log:
        print(datetime.now(), *args, file=log)
