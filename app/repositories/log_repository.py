from app.models.alert_logs import AlertLog


def create_alert_log(db, log_data):
    log = AlertLog(
        alert_id=log_data.get("alert_id"),
        sensor_id=log_data.get("sensor_id"),
        message=log_data.get("message"),
        severity=log_data.get("severity"),
        resolved=log_data.get("resolved", False)
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log
