from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.data import SensorDataSchema
from app.services.data_service import save_data, process_rules


router = APIRouter(prefix="/data", tags=["Data"])


@router.post("/")
def insert_data(
    data: SensorDataSchema,
    db: Session = Depends(get_db)
):
    record = save_data(db, data)

    alerts = process_rules(db, data)

    return {
        "message": "Data stored successfully",
        "data_id": record.id,
        "alerts_generated": [
            {
                "id": alert.id,
                "sensor_id": alert.sensor_id,
                "message": alert.message,
                "severity": alert.severity,
                "is_resolved": alert.is_resolved
            }
            for alert in alerts
        ]
    }
