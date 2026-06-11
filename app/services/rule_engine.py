from app.models.rule import Rule
from app.repositories.alert_repository import create_alert
from app.repositories.log_repository import create_alert_log


DEFAULT_TEMPERATURE_MAX = 200
DEFAULT_HUMIDITY_MAX = 100


def create_alert_with_log(db, sensor_id, message, severity="high"):
    alert = create_alert(db, {
        "sensor_id": sensor_id,
        "message": message,
        "severity": severity
    })

    create_alert_log(db, {
        "alert_id": alert.id,
        "sensor_id": sensor_id,
        "message": alert.message,
        "severity": alert.severity,
        "resolved": False
    })

    return alert


def get_rule(db, sensor_type):
    return (
        db.query(Rule)
        .filter(Rule.sensor_type == sensor_type)
        .first()
    )


def check_rules(db, data):
    generated_alerts = []

    print("Rule engine checking data:", data)

    # Temperature check
    temperature_rule = get_rule(db, "temperature")

    if temperature_rule and temperature_rule.max_value is not None:
        temp_max = temperature_rule.max_value
        temp_severity = temperature_rule.severity or "high"
    else:
        temp_max = DEFAULT_TEMPERATURE_MAX
        temp_severity = "high"

    if data.temperature > temp_max:
        alert = create_alert_with_log(
            db=db,
            sensor_id=data.sensor_id,
            message=f"Temperature exceeded threshold. Current value: {data.temperature}, Max allowed: {temp_max}",
            severity=temp_severity
        )
        generated_alerts.append(alert)

    # Humidity check
    humidity_rule = get_rule(db, "humidity")

    if humidity_rule and humidity_rule.max_value is not None:
        humidity_max = humidity_rule.max_value
        humidity_severity = humidity_rule.severity or "high"
    else:
        humidity_max = DEFAULT_HUMIDITY_MAX
        humidity_severity = "high"

    if data.humidity > humidity_max:
        alert = create_alert_with_log(
            db=db,
            sensor_id=data.sensor_id,
            message=f"Humidity exceeded threshold. Current value: {data.humidity}, Max allowed: {humidity_max}",
            severity=humidity_severity
        )
        generated_alerts.append(alert)

    # Door check
    if data.door_open:
        alert = create_alert_with_log(
            db=db,
            sensor_id=data.sensor_id,
            message="Door is opened",
            severity="high"
        )
        generated_alerts.append(alert)

    print("Generated alerts count:", len(generated_alerts))

    return generated_alerts
