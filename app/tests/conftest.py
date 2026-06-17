import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT_DIR))

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)