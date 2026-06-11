from app.repositories.alert_repository import create_alert

def trigger_alert(db, sensor_id, value, message, severity="high"):
    return create_alert(db, {
        "sensor_id": sensor_id,
        "value": value,
        "message": message,
        "severity": severity
    })
    