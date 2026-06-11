from pathlib import Path
import subprocess
import sys
from fastapi.responses import RedirectResponse
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db.base import Base
from app.configurations.db import engine
from app.db.session import SessionLocal

from app.routes import (
    data,
    alerts,
    sensors,
    warehouses,
    storage_unit,
    metrics,
    dashboard,
    rules,
    auth
)

from app.models import (
    sensor_data,
    rule,
    alert,
    alert_logs,
    sensor as sensor_model,
    warehouse as warehouse_model,
    storage_unit as storage_unit_model,
    user as user_model
)

from app.models.user import User
from app.services.auth_utils import hash_password
from app.routes import auth

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
SIMULATOR_FILE = BASE_DIR / "simulator" / "data_generator.py"

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cold Storage Monitoring System")

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)


def create_default_admin():
    db = SessionLocal()

    try:
        admin = db.query(User).filter(User.username == "admin").first()

        if not admin:
            admin_user = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin"
            )

            db.add(admin_user)
            db.commit()

            print("Default admin created: username=admin password=admin123")

    finally:
        db.close()


create_default_admin()


app.include_router(auth.router)
app.include_router(data.router)
app.include_router(alerts.router)
app.include_router(sensors.router)
app.include_router(warehouses.router)
app.include_router(storage_unit.router)
app.include_router(metrics.router)
app.include_router(rules.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return RedirectResponse(url="/login", status_code=303)

@app.on_event("startup")
def start_simulator():
    if not SIMULATOR_FILE.exists():
        print("Simulator file not found:", SIMULATOR_FILE)
        return

    if not hasattr(app.state, "simulator_process"):
        app.state.simulator_process = subprocess.Popen(
            [sys.executable, "-u", str(SIMULATOR_FILE)],
            cwd=str(BASE_DIR)
        )
        print("Simulator started automatically.")


@app.on_event("shutdown")
def stop_simulator():
    simulator_process = getattr(app.state, "simulator_process", None)

    if simulator_process:
        simulator_process.terminate()
        print("Simulator stopped.")