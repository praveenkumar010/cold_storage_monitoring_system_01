from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.sensor_data import SensorData
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.alert import Alert


router=APIRouter(prefix="/metrics",tags=["Metrics"])

@router.get("/latest")
def latest_data(db:Session=Depends(get_db)):
    data=db.query(SensorData).order_by(SensorData.created_at.desc()).limit(10).all()
    return data

@router.get("/avg-temp")
def avg_temp(db:Session=Depends(get_db)):
    avg_temp=db.query(func.avg(SensorData.temperature)).scalar()
    return {"avg_temp":avg_temp}

@router.get("/temp_trend")
def temp_trend(limit:int=20,db:Session=Depends(get_db)):
    return (db.query(SensorData).order_by(SensorData.created_at.desc()).limit(limit).all())

@router.get("/weekly-alerts")
def weekly_alerts(db: Session = Depends(get_db)):
    last_7_days = datetime.utcnow() - timedelta(days=7)
    data = (
        db.query(func.date(Alert.created_at), func.count(Alert.id))
        .filter(Alert.created_at >= last_7_days)
        .group_by(func.date(Alert.created_at))
        .all()
    )

    return [{"date": str(d[0]), "count": d[1]} for d in data]
