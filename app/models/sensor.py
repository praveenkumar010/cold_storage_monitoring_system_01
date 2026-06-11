from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)

    storage_unit_id = Column(Integer, ForeignKey("storage_units.id"))

    sensor_type = Column(String(100))
    source = Column(String(100))
    status = Column(String(50), default="active")