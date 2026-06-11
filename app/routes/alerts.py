from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.alert import Alert
from app.models.alert_logs import AlertLog

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/")
def get_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).all()


@router.put("/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):

    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        return {"error": "Not found"}

    alert.is_resolved = True

    log = AlertLog(
        alert_id=alert.id,
        sensor_id=alert.sensor_id,
        message=alert.message,
        severity=alert.severity,
        resolved=True
    )

    db.add(log)
    db.commit()

    return {"message": "Resolved ✅"}