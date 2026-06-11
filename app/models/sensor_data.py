from sqlalchemy import Integer,Column, String, ForeignKey, Float, DateTime,Boolean
from app.db.base import Base
from datetime import datetime

class SensorData(Base):
    __tablename__="sensor_data"
    
    id=Column(Integer, primary_key=True)
    sensor_id=Column(Integer,ForeignKey("sensors.id"))
    temperature=Column(Float)
    humidity=Column(Float)
    door_open=Column(Boolean,default=False)
    created_at=Column(DateTime,default=datetime.utcnow)