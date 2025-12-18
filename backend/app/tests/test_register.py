import os
import pathlib

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# configure env before imports
test_db_path = pathlib.Path(__file__).parent / "test.db"
DATABASE_URL = f"sqlite+pysqlite:///{test_db_path}"

os.environ.setdefault("DATABASE_URL", DATABASE_URL)
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("HASH_SCHEME", "argon2")
os.environ.setdefault("ARGON2_TIME_COST", "2")
os.environ.setdefault("ARGON2_MEMORY_COST", "512")
os.environ.setdefault("ARGON2_PARALLELISM", "2")

from app.main import app  # noqa: E402
from app.database import Base, get_db  # noqa: E402

engine = create_engine(DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_successful_registration():
    response = client.post(
        "/api/register",
        json={"login": "User123", "password": "StrongPass1!"},
    )
    assert response.status_code == 201
    assert response.json() == {"message": "user создан"}


def test_duplicate_login():
    payload = {"login": "duplicate", "password": "StrongPass1!"}
    first = client.post("/api/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/register", json=payload)
    assert second.status_code == 409
    assert "Login already exists" in second.json()["detail"]


def test_weak_password_validation():
    response = client.post(
        "/api/register",
        json={"login": "weakpass", "password": "short"},
    )
    assert response.status_code == 422
    assert "Password must be at least 8 characters" in str(response.json()["detail"])
