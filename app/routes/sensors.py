from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.sensor import Sensor


router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.get("/")
def get_sensors(db: Session = Depends(get_db)):
    sensors = (
        db.query(Sensor)
        .order_by(Sensor.id.desc())
        .all()
    )

    return [
        {
            "id": sensor.id,
            "storage_unit_id": sensor.storage_unit_id,
            "sensor_type": sensor.sensor_type,
            "source": sensor.source,
            "status": sensor.status
        }
        for sensor in sensors
    ]