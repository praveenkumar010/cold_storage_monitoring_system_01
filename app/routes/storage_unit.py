from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.storage_unit import StorageUnit
from app.schemas.storage_unit import StorageUnitCreate

router = APIRouter(prefix="/storage-units", tags=["Storage Units"])


@router.post("/")
def create_storage_unit(data: StorageUnitCreate, db: Session = Depends(get_db)):
    unit = StorageUnit(
        warehouse_id=data.warehouse_id,
        name=data.name,
        unit_type=data.unit_type
    )

    db.add(unit)
    db.commit()
    db.refresh(unit)

    return unit


@router.get("/")
def get_storage_units(db: Session = Depends(get_db)):
    return db.query(StorageUnit).all()