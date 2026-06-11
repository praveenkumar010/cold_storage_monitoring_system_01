from datetime import datetime

def current_time():
    return datetime.utcnow()


def format_alert_message(sensor_type, value):
    return f"{sensor_type} crossed threshold: {value}"
