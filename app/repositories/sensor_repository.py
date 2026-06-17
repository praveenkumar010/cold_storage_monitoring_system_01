from app.models.sensor_data import SensorData

def create_sensor_data(db, data):
    record = SensorData(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
