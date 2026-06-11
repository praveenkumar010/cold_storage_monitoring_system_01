import random

from app.models.storage_unit import StorageUnit
from app.models.sensor import Sensor
from app.schemas.data import SensorDataSchema
from app.services.data_service import save_data, process_rules


def should_trigger_alert(chance_percent: int):
    return random.randint(1, 100) <= chance_percent


def generate_random_payload(sensor):
    sensor_type = sensor.sensor_type

    temperature = round(random.uniform(2, 180), 2)
    humidity = round(random.uniform(40, 95), 2)
    door_open = False

    if sensor_type == "temperature":
        if should_trigger_alert(70):
            temperature = round(random.uniform(201, 350), 2)

    elif sensor_type == "humidity":
        if should_trigger_alert(70):
            humidity = round(random.uniform(101, 160), 2)

    elif sensor_type == "door_open":
        if should_trigger_alert(70):
            door_open = True

    return SensorDataSchema(
        sensor_id=sensor.id,
        temperature=temperature,
        humidity=humidity,
        door_open=door_open
    )


def generate_random_alert_for_sensor(db, sensor):
    

    data = generate_random_payload(sensor)

    record = save_data(db, data)
    alerts = process_rules(db, data)

    print("Random data generated for sensor:", sensor.id, sensor.sensor_type)
    print("Data ID:", record.id)
    print("Alerts generated:", len(alerts))

    return alerts


def generate_random_alerts_for_warehouse(db, warehouse_id: int):
    

    storage_units = (
        db.query(StorageUnit)
        .filter(StorageUnit.warehouse_id == warehouse_id)
        .all()
    )

    storage_unit_ids = [unit.id for unit in storage_units]

    if not storage_unit_ids:
        print("No storage units found for warehouse:", warehouse_id)
        return []

    sensors = (
        db.query(Sensor)
        .filter(Sensor.storage_unit_id.in_(storage_unit_ids))
        .filter(Sensor.status == "active")
        .all()
    )

    if not sensors:
        print("No sensors found for warehouse:", warehouse_id)
        return []

    generated_alerts = []

    selected_sensor = random.choice(sensors)

    alerts = generate_random_alert_for_sensor(db, selected_sensor)

    generated_alerts.extend(alerts)

    return generated_alerts