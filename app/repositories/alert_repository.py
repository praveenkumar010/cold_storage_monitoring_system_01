from app.models.alert import Alert


def create_alert(db, alert_data):
    alert = Alert(
        sensor_id=alert_data["sensor_id"],
        message=alert_data["message"],
        severity=alert_data.get("severity", "high"),
        is_resolved=False
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert
