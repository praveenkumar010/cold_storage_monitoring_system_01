from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.post("/")
def create_warehouse(data: WarehouseCreate, db: Session = Depends(get_db)):
    warehouse = Warehouse(
        name=data.name,
        location=data.location
    )

    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)

    return warehouse


@router.get("/")
def get_warehouses(db: Session = Depends(get_db)):
    return db.query(Warehouse).all()
