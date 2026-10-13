import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        response = test_client.post("/api/auth/register", json={"username": "primary_user", "password": "primary-pass-123"})
        assert response.status_code == 201
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def payload():
    return {
        "patient_name": " Alex Morgan ",
        "appointment_datetime": "2030-06-15T10:00:00",
        "doctor": "Dr. Emily Carter",
        "appointment_type": "General Consultation",
        "status": "Scheduled",
    }
