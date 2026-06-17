from app.models.sensor_data import SensorData
from app.services.rule_engine import check_rules


def save_data(db, data):
    sensor_data = SensorData(
        sensor_id=data.sensor_id,
        temperature=data.temperature,
        humidity=data.humidity,
        door_open=data.door_open
    )

    db.add(sensor_data)
    db.commit()
    db.refresh(sensor_data)

    return sensor_data


def process_rules(db, data):
    return check_rules(db, data)
