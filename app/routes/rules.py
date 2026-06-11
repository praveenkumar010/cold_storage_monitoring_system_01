from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.rule import Rule

router = APIRouter(prefix="/rules", tags=["Rules"])


@router.post("/")
def create_rule(
    sensor_type: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    severity: str = "high",
    db: Session = Depends(get_db)
):
    rule = Rule(
        sensor_type=sensor_type,
        min_value=min_value,
        max_value=max_value,
        severity=severity
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    return rule


@router.get("/")
def get_rules(db: Session = Depends(get_db)):
    return db.query(Rule).all()