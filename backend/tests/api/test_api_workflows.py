import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db
from app.db.models import User

# File-based SQLite for testing across connection threads
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_studypal.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("./test_studypal.db"):
        try:
            os.remove("./test_studypal.db")
        except Exception:
            pass


client = TestClient(app)


def test_health_endpoints():
    live_res = client.get("/health/live")
    assert live_res.status_code == 200
    assert live_res.json()["status"] == "alive"

    ready_res = client.get("/health/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["database_connected"] is True


def test_auth_workflow():
    # Register
    reg_res = client.post("/api/v1/auth/register", json={
        "email": "student@example.com",
        "password": "strongpassword123",
        "display_name": "Test Student"
    })
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert "access_token" in data
    token = data["access_token"]

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "student@example.com", "password": "strongpassword123"}
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # Get Me
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "student@example.com"


def test_courses_crud():
    # Register student
    reg = client.post("/api/v1/auth/register", json={
        "email": "course_creator@example.com",
        "password": "password123",
        "display_name": "Course Creator"
    }).json()
    token = reg["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Course
    create_res = client.post("/api/v1/courses", json={
        "name": "Machine Learning Fundamentals",
        "description": "Introduction to supervised and unsupervised learning"
    }, headers=headers)
    assert create_res.status_code == 201
    course_id = create_res.json()["id"]

    # List Courses
    list_res = client.get("/api/v1/courses", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # Update Course
    update_res = client.patch(f"/api/v1/courses/{course_id}", json={
        "name": "Advanced Machine Learning"
    }, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Advanced Machine Learning"

    # Delete Course
    del_res = client.delete(f"/api/v1/courses/{course_id}", headers=headers)
    assert del_res.status_code == 204
