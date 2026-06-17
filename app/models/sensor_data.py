from sqlalchemy import (Column,Integer,Float,Boolean,DateTime,ForeignKey)
from datetime import datetime, timezone
from app.db.base import Base


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)

    sensor_id = Column( Integer, ForeignKey("sensors.id") )

    temperature = Column(Float, nullable=True)

    humidity = Column(Float, nullable=True)

    door_open = Column(Boolean, nullable=True)

    created_at = Column(DateTime,default=datetime.utcnow)