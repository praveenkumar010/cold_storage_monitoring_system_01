from fastapi import APIRouter, Depends, Request, Form, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db

from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.storage_unit import StorageUnit
from app.models.sensor import Sensor
from app.models.sensor_data import SensorData
from app.models.alert import Alert
from app.models.alert_logs import AlertLog


router = APIRouter(tags=["Frontend"])

templates = Jinja2Templates(directory="templates")


# ======================================================
# CURRENT USER
# ======================================================

def get_logged_in_user(user_id: Optional[str], db: Session):
    if not user_id:
        return None

    try:
        return db.query(User).filter(User.id == int(user_id)).first()
    except Exception:
        return None


# ======================================================
# USER-SPECIFIC DATA
# ======================================================

def get_user_warehouses(db: Session, user_id: int):
    return (
        db.query(Warehouse)
        .filter(Warehouse.owner_id == user_id)
        .order_by(Warehouse.id.desc())
        .all()
    )


def get_user_storage_units(db: Session, user_id: int):
    warehouses = get_user_warehouses(db, user_id)
    warehouse_ids = [warehouse.id for warehouse in warehouses]

    if not warehouse_ids:
        return []

    return (
        db.query(StorageUnit)
        .filter(StorageUnit.warehouse_id.in_(warehouse_ids))
        .order_by(StorageUnit.id.desc())
        .all()
    )


def get_user_sensors(db: Session, user_id: int):
    storage_units = get_user_storage_units(db, user_id)
    storage_unit_ids = [unit.id for unit in storage_units]

    if not storage_unit_ids:
        return []

    return (
        db.query(Sensor)
        .filter(Sensor.storage_unit_id.in_(storage_unit_ids))
        .order_by(Sensor.id.desc())
        .all()
    )


def get_user_sensor_ids(db: Session, user_id: int):
    sensors = get_user_sensors(db, user_id)
    return [sensor.id for sensor in sensors]


# ======================================================
# CHART HELPERS
# ======================================================

def build_alert_type_chart(alerts):
    """
    Only include:
    - temperature
    - humidity
    - door
    No 'other'
    """

    temperature_count = 0
    humidity_count = 0
    door_count = 0

    for alert in alerts:
        message = (alert.message or "").lower()

        if "temperature" in message:
            temperature_count += 1
        elif "humidity" in message:
            humidity_count += 1
        elif "door" in message:
            door_count += 1

    total = temperature_count + humidity_count + door_count

    if total == 0:
        return {
            "temperature": 0,
            "humidity": 0,
            "door": 0,
            "pie_gradient": "#e5e5e5"
        }

    temp_pct = (temperature_count / total) * 100
    humidity_pct = (humidity_count / total) * 100
    door_pct = (door_count / total) * 100

    pie_gradient = (
        "conic-gradient("
        f"#111111 0% {temp_pct}%, "
        f"#555555 {temp_pct}% {temp_pct + humidity_pct}%, "
        f"#999999 {temp_pct + humidity_pct}% 100%"
        ")"
    )

    return {
        "temperature": temperature_count,
        "humidity": humidity_count,
        "door": door_count,
        "pie_gradient": pie_gradient
    }


def build_storage_unit_alert_chart(db: Session, storage_units, alerts):
    sensors = db.query(Sensor).all()

    sensor_to_unit = {}

    for sensor in sensors:
        sensor_to_unit[sensor.id] = sensor.storage_unit_id

    unit_counts = {}

    for unit in storage_units:
        unit_counts[unit.id] = {
            "name": unit.name,
            "count": 0
        }

    for alert in alerts:
        # only count temperature/humidity/door alerts
        message = (alert.message or "").lower()

        if (
            "temperature" not in message and
            "humidity" not in message and
            "door" not in message
        ):
            continue

        unit_id = sensor_to_unit.get(alert.sensor_id)

        if unit_id in unit_counts:
            unit_counts[unit_id]["count"] += 1

    max_count = max([data["count"] for data in unit_counts.values()], default=0)

    chart_data = []

    for unit_id, data in unit_counts.items():
        count = data["count"]

        if max_count == 0:
            width = 8
        else:
            width = max((count / max_count) * 100, 8)

        chart_data.append({
            "storage_unit": data["name"],
            "count": count,
            "width": round(width, 2)
        })

    return chart_data


# ======================================================
# DELETE HELPERS
# ======================================================

def delete_sensor_dependencies(db: Session, sensor_id: int):
    db.query(AlertLog).filter(AlertLog.sensor_id == sensor_id).delete(synchronize_session=False)
    db.query(Alert).filter(Alert.sensor_id == sensor_id).delete(synchronize_session=False)
    db.query(SensorData).filter(SensorData.sensor_id == sensor_id).delete(synchronize_session=False)


def delete_sensor_with_dependencies(db: Session, sensor_id: int):
    delete_sensor_dependencies(db, sensor_id)
    db.query(Sensor).filter(Sensor.id == sensor_id).delete(synchronize_session=False)


def delete_storage_unit_with_dependencies(db: Session, storage_unit_id: int):
    sensors = (
        db.query(Sensor)
        .filter(Sensor.storage_unit_id == storage_unit_id)
        .all()
    )

    for sensor in sensors:
        delete_sensor_with_dependencies(db, sensor.id)

    db.query(StorageUnit).filter(StorageUnit.id == storage_unit_id).delete(synchronize_session=False)


def delete_warehouse_with_dependencies(db: Session, warehouse_id: int):
    storage_units = (
        db.query(StorageUnit)
        .filter(StorageUnit.warehouse_id == warehouse_id)
        .all()
    )

    for unit in storage_units:
        delete_storage_unit_with_dependencies(db, unit.id)

    db.query(Warehouse).filter(Warehouse.id == warehouse_id).delete(synchronize_session=False)


# ======================================================
# DASHBOARD
# ======================================================

@router.get("/dashboard")
def dashboard(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    current_user = get_logged_in_user(user_id, db)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    # ==================================================
    # ADMIN VIEW
    # ==================================================
    if current_user.role == "admin":
        users = db.query(User).order_by(User.id.desc()).all()
        user_lookup = {user.id: user.username for user in users}

        all_warehouses = db.query(Warehouse).order_by(Warehouse.id.desc()).all()
        all_storage_units = db.query(StorageUnit).order_by(StorageUnit.id.desc()).all()

        alerts = db.query(Alert).order_by(Alert.created_at.desc()).all()
        all_sensors = db.query(Sensor).all()

        sensor_lookup = {
            sensor.id: sensor
            for sensor in all_sensors
        }

        storage_lookup = {
            unit.id: unit
            for unit in all_storage_units
        }

        warehouse_lookup = {
            warehouse.id: warehouse
            for warehouse in all_warehouses
        }

        for alert in alerts:

            sensor = sensor_lookup.get(alert.sensor_id)

            if sensor:

                alert.sensor_name = (
                    sensor.sensor_type
                    .replace("_", " ")
                    .title()
                )

                storage_unit = storage_lookup.get(
                    sensor.storage_unit_id
                )

                if storage_unit:

                    alert.storage_unit_name = storage_unit.name

                    warehouse = warehouse_lookup.get(
                        storage_unit.warehouse_id
                    )

                    if warehouse:
                        alert.warehouse_name = warehouse.name
                    else:
                        alert.warehouse_name = "Unknown"

                else:
                    alert.storage_unit_name = "Unknown"
                    alert.warehouse_name = "Unknown"

            else:
                alert.sensor_name = "Unknown"
                alert.storage_unit_name = "Unknown"
                alert.warehouse_name = "Unknown"

        alert_logs = db.query(AlertLog).order_by(AlertLog.created_at.desc()).all()

        active_alerts = [alert for alert in alerts if not alert.is_resolved]
        resolved_alerts = [alert for alert in alerts if alert.is_resolved]
        high_alerts = [alert for alert in alerts if alert.severity == "high"]

        context = {
            "request": request,
            "current_user": current_user,
            "users": users,
            "user_lookup": user_lookup,

            "warehouses": all_warehouses,
            "storage_units": [],
            "sensors": [],

            "alerts": alerts[:10],
            "active_alerts": active_alerts,
            "resolved_alerts": resolved_alerts,
            "alert_logs": alert_logs,

            "warehouse_count": len(all_warehouses),
            "storage_unit_count": 0,
            "sensor_count": 0,

            "total_alerts": len(alerts),
            "active_count": len(active_alerts),
            "resolved_count": len(resolved_alerts),
            "high_count": len(high_alerts),

            "alert_type_chart": build_alert_type_chart(alerts),
            "storage_unit_alert_chart": build_storage_unit_alert_chart(
                db=db,
                storage_units=all_storage_units,
                alerts=alerts
            )
        }

        return templates.TemplateResponse(request, "dashboard.html", context)


    # ==================================================
    # USER VIEW
    # ==================================================
    warehouses = get_user_warehouses(db, current_user.id)
    storage_units = get_user_storage_units(db, current_user.id)
    sensors = get_user_sensors(db, current_user.id)

    user_sensor_ids = [sensor.id for sensor in sensors]

    if user_sensor_ids:
        alerts = (
            db.query(Alert)
            .filter(Alert.sensor_id.in_(user_sensor_ids))
            .order_by(Alert.created_at.desc())
            .all()
        )

        alert_logs = (
            db.query(AlertLog)
            .filter(AlertLog.sensor_id.in_(user_sensor_ids))
            .order_by(AlertLog.created_at.desc())
            .all()
        )
    else:
        alerts = []
        alert_logs = []

    active_alerts = [alert for alert in alerts if not alert.is_resolved]
    resolved_alerts = [alert for alert in alerts if alert.is_resolved]
    high_alerts = [alert for alert in alerts if alert.severity == "high"]
    sensor_lookup = {
        sensor.id: sensor
        for sensor in sensors
    }

    storage_lookup = {
        unit.id: unit
        for unit in storage_units
    }

    warehouse_lookup = {
        warehouse.id: warehouse
        for warehouse in warehouses
    }

    for alert in alerts:

        sensor = sensor_lookup.get(alert.sensor_id)

        if sensor:
            alert.sensor_name = (sensor.sensor_type.replace("_", " ").title() )

            storage_unit = storage_lookup.get(sensor.storage_unit_id)

            if storage_unit:
                alert.storage_unit_name = storage_unit.name

                warehouse = warehouse_lookup.get(storage_unit.warehouse_id)

                if warehouse:
                    alert.warehouse_name = warehouse.name
                else:
                    alert.warehouse_name = "Unknown"

            else:
                alert.storage_unit_name = "Unknown"
                alert.warehouse_name = "Unknown"

        else:
            alert.sensor_name = "Unknown"
            alert.storage_unit_name = "Unknown"
            alert.warehouse_name = "Unknown"


    context = {
        "request": request,
        "current_user": current_user,
        "users": [],

        "warehouses": warehouses,
        "storage_units": storage_units,
        "sensors": sensors,

        "alerts": alerts[:10],
        "active_alerts": active_alerts,
        "resolved_alerts": resolved_alerts,
        "alert_logs": alert_logs,

        "warehouse_count": len(warehouses),
        "storage_unit_count": len(storage_units),
        "sensor_count": len(sensors),

        "total_alerts": len(alerts),
        "active_count": len(active_alerts),
        "resolved_count": len(resolved_alerts),
        "high_count": len(high_alerts),

        "alert_type_chart": build_alert_type_chart(alerts),
        "storage_unit_alert_chart": build_storage_unit_alert_chart(
            db=db,
            storage_units=storage_units,
            alerts=alerts
        )
    }

    return templates.TemplateResponse(request, "dashboard.html", context)


# ======================================================
# ADMIN: CREATE & ASSIGN WAREHOUSE
# ======================================================

@router.post("/ui/admin/warehouses/create")
def admin_create_warehouse_for_user(
    owner_id: int = Form(...),
    name: str = Form(...),
    location: str = Form(...),
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    current_user = get_logged_in_user(user_id, db)

    if not current_user or current_user.role != "admin":
        return RedirectResponse(url="/dashboard", status_code=303)

    owner = db.query(User).filter(User.id == owner_id).first()

    if not owner or owner.role == "admin":
        return RedirectResponse(url="/dashboard", status_code=303)

    warehouse = Warehouse(
        owner_id=owner_id,
        name=name,
        location=location
    )

    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)

    return RedirectResponse(url="/dashboard", status_code=303)


# ======================================================
# ADMIN: DELETE WAREHOUSE
# ======================================================

@router.post("/ui/admin/warehouses/{warehouse_id}/delete")
def delete_warehouse_from_ui(
    warehouse_id: int,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    current_user = get_logged_in_user(user_id, db)

    if not current_user or current_user.role != "admin":
        return RedirectResponse(url="/dashboard", status_code=303)

    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()

    if not warehouse:
        return RedirectResponse(url="/dashboard", status_code=303)

    delete_warehouse_with_dependencies(db, warehouse_id)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)


# ======================================================
# USER: CREATE STORAGE UNIT
# AUTO CREATE 3 DEFAULT SENSORS
# ======================================================

@router.post("/ui/storage-units/create")
def create_storage_unit_from_ui(
    warehouse_id: int = Form(...),
    name: str = Form(...),
    unit_type: str = Form(...),
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    current_user = get_logged_in_user(user_id, db)

    if not current_user or current_user.role == "admin":
        return RedirectResponse(url="/dashboard", status_code=303)

    warehouse = (
        db.query(Warehouse)
        .filter(Warehouse.id == warehouse_id)
        .filter(Warehouse.owner_id == current_user.id)
        .first()
    )

    if not warehouse:
        return RedirectResponse(url="/dashboard", status_code=303)

    storage_unit = StorageUnit(
        warehouse_id=warehouse_id,
        name=name,
        unit_type=unit_type
    )

    db.add(storage_unit)
    db.commit()
    db.refresh(storage_unit)

    # ✅ Automatically create default sensors for all storage units
    default_sensors = [
        Sensor(
            storage_unit_id=storage_unit.id,
            sensor_type="temperature",
            source="default",
            status="active"
        ),
        Sensor(
            storage_unit_id=storage_unit.id,
            sensor_type="humidity",
            source="default",
            status="active"
        ),
        Sensor(
            storage_unit_id=storage_unit.id,
            sensor_type="door_open",
            source="default",
            status="active"
        )
    ]

    db.add_all(default_sensors)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)


# ======================================================
# USER: DELETE STORAGE UNIT
# ======================================================

@router.post("/ui/storage-units/{storage_unit_id}/delete")
def delete_storage_unit_from_ui(
    storage_unit_id: int,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    current_user = get_logged_in_user(user_id, db)

    if not current_user or current_user.role == "admin":
        return RedirectResponse(url="/dashboard", status_code=303)

    storage_unit = (
        db.query(StorageUnit)
        .filter(StorageUnit.id == storage_unit_id)
        .first()
    )

    if not storage_unit:
        return RedirectResponse(url="/dashboard", status_code=303)

    warehouse = (
        db.query(Warehouse)
        .filter(Warehouse.id == storage_unit.warehouse_id)
        .filter(Warehouse.owner_id == current_user.id)
        .first()
    )

    if not warehouse:
        return RedirectResponse(url="/dashboard", status_code=303)

    delete_storage_unit_with_dependencies(db, storage_unit_id)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)


# ======================================================
# USER: DELETE SENSOR
# ======================================================

@router.post("/ui/sensors/{sensor_id}/delete")
def delete_sensor_from_ui(
    sensor_id: int,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    current_user = get_logged_in_user(user_id, db)

    if not current_user or current_user.role == "admin":
        return RedirectResponse(url="/dashboard", status_code=303)

    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()

    if not sensor:
        return RedirectResponse(url="/dashboard", status_code=303)

    storage_unit = (
        db.query(StorageUnit)
        .filter(StorageUnit.id == sensor.storage_unit_id)
        .first()
    )

    if not storage_unit:
        return RedirectResponse(url="/dashboard", status_code=303)

    warehouse = (
        db.query(Warehouse)
        .filter(Warehouse.id == storage_unit.warehouse_id)
        .filter(Warehouse.owner_id == current_user.id)
        .first()
    )

    if not warehouse:
        return RedirectResponse(url="/dashboard", status_code=303)

    delete_sensor_with_dependencies(db, sensor_id)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)


# ======================================================
# USER ONLY: RESOLVE ALERT
# ======================================================

@router.post("/ui/alerts/{alert_id}/resolve")
def resolve_alert_from_dashboard(
    alert_id: int,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    current_user = get_logged_in_user(user_id, db)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    if current_user.role == "admin":
        return RedirectResponse(url="/dashboard", status_code=303)

    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        return RedirectResponse(url="/dashboard", status_code=303)

    user_sensor_ids = get_user_sensor_ids(db, current_user.id)

    if alert.sensor_id not in user_sensor_ids:
        return RedirectResponse(url="/dashboard", status_code=303)

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

    return RedirectResponse(url="/dashboard", status_code=303)