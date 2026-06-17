from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base


class StorageUnit(Base):
    __tablename__ = "storage_units"

    id = Column(Integer, primary_key=True, index=True)

    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))

    name = Column(String(100))
    unit_type = Column(String(100))