def create(client, payload, **changes):
    return client.post("/api/appointments", json={**payload, **changes})


def test_authentication_and_account_data_isolation(client, payload):
    appointment = create(client, payload)
    assert appointment.status_code == 201

    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as second_user:
        registration = second_user.post("/api/auth/register", json={"username": "second_user", "password": "second-pass-123"})
        assert registration.status_code == 201
        assert second_user.get("/api/auth/me").json()["username"] == "second_user"
        assert second_user.get("/api/appointments").json() == []
        assert second_user.get(f"/api/appointments/{appointment.json()['id']}").status_code == 404

        # Appointment records are private, but doctor availability is shared across accounts.
        assert create(second_user, payload).status_code == 409
        assert create(second_user, payload, appointment_datetime="2030-06-15T10:30:00").status_code == 201
        assert len(client.get("/api/appointments").json()) == 1
        assert len(second_user.get("/api/appointments").json()) == 1

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/appointments").status_code == 401
    assert client.post("/api/auth/login", json={"username": "primary_user", "password": "primary-pass-123"}).status_code == 200


def test_appointments_require_login(client):
    client.post("/api/auth/logout")
    assert client.get("/api/appointments").status_code == 401
    assert client.get("/api/appointments/stats/summary").status_code == 401


def test_account_update_changes_username_and_password(client):
    changed = client.put("/api/auth/account", json={
        "current_password": "primary-pass-123",
        "username": "renamed_user",
        "new_password": "updated-pass-456",
    })
    assert changed.status_code == 200
    assert changed.json()["username"] == "renamed_user"
    assert client.get("/api/auth/me").json()["username"] == "renamed_user"

    assert client.put("/api/auth/account", json={
        "current_password": "wrong-password", "username": "another_name",
    }).status_code == 401
    assert client.put("/api/auth/account", json={
        "current_password": "updated-pass-456", "new_password": "short",
    }).status_code == 422
    assert client.put("/api/auth/account", json={
        "current_password": "updated-pass-456", "username": "!bad name",
    }).status_code == 422

    client.post("/api/auth/logout")
    assert client.post("/api/auth/login", json={
        "username": "renamed_user", "password": "updated-pass-456",
    }).status_code == 200


def test_account_update_rejects_username_owned_by_another_user(client):
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as second_user:
        second_user.post("/api/auth/register", json={"username": "second_user", "password": "second-pass-123"})
        response = client.put("/api/auth/account", json={
            "current_password": "primary-pass-123", "username": "second_user",
        })
        assert response.status_code == 409


def test_create_trims_name_and_defaults_status(client, payload):
    payload.pop("status")
    response = client.post("/api/appointments", json=payload)
    assert response.status_code == 201
    assert response.json()["patient_name"] == "Alex Morgan"
    assert response.json()["status"] == "Scheduled"


def test_validation_rejects_bad_fields(client, payload):
    for changes in ({"patient_name": "  "}, {"doctor": None}, {"appointment_type": "Other"}, {"status": "Waiting"}, {"appointment_datetime": "not-a-date"}):
        assert create(client, payload, **changes).status_code == 422
    missing_doctor = dict(payload)
    del missing_doctor["doctor"]
    assert client.post("/api/appointments", json=missing_doctor).status_code == 422


def test_conflicts_back_to_back_other_doctor_and_cancelled(client, payload):
    assert create(client, payload).status_code == 201
    assert create(client, payload, appointment_datetime="2030-06-15T10:15:00").status_code == 409
    assert create(client, payload, appointment_datetime="2030-06-15T10:30:00").status_code == 201
    assert create(client, payload, appointment_datetime="2030-06-15T10:15:00", doctor="Dr. James Wilson").status_code == 201
    assert create(client, payload, appointment_datetime="2030-06-15T10:15:00", status="Cancelled").status_code == 201
    assert create(client, payload, appointment_datetime="2030-06-15T11:15:00").status_code == 201
    assert create(client, payload, appointment_datetime="2030-06-15T12:00:00", status="Completed").status_code == 201
    assert create(client, payload, appointment_datetime="2030-06-15T12:15:00").status_code == 201
    assert create(client, payload, appointment_datetime="2030-06-15T10:15:00", status="Completed").status_code == 201


def test_retrieval_filters_and_stats(client, payload):
    one = create(client, payload).json()
    create(client, payload, patient_name="Jamie Taylor", appointment_datetime="2030-06-16T10:00:00", doctor="Dr. James Wilson", appointment_type="Follow-up", status="Completed")
    assert client.get("/api/appointments").status_code == 200
    assert client.get(f"/api/appointments/{one['id']}").json()["patient_name"] == "Alex Morgan"
    assert client.get("/api/appointments/999").status_code == 404
    assert len(client.get("/api/appointments?search=Alex").json()) == 1
    assert len(client.get("/api/appointments?search=James").json()) == 1
    assert len(client.get("/api/appointments?status=Completed").json()) == 1
    assert len(client.get("/api/appointments?appointment_type=Follow-up").json()) == 1
    assert len(client.get("/api/appointments?doctor=Dr.%20James%20Wilson").json()) == 1
    assert len(client.get("/api/appointments?date=2030-06-15").json()) == 1
    assert len(client.get("/api/appointments?search=Alex&status=Scheduled&date=2030-06-15").json()) == 1
    assert client.get("/api/appointments?search=nobody").json() == []
    assert client.get("/api/appointments/stats/summary").json()["total"] == 2


def test_update_conflict_self_exclusion_and_delete(client, payload):
    first = create(client, payload).json()
    second = create(client, payload, appointment_datetime="2030-06-15T11:00:00").json()
    assert client.put(f"/api/appointments/{first['id']}", json={**payload, "appointment_datetime": "2030-06-15T11:00:00"}).status_code == 409
    same = client.put(f"/api/appointments/{first['id']}", json={**payload, "patient_name": "Updated"})
    assert same.status_code == 200
    assert same.json()["id"] == first["id"]
    assert client.put("/api/appointments/999", json=payload).status_code == 404
    assert client.put(f"/api/appointments/{first['id']}", json={**payload, "status": "Invalid"}).status_code == 422
    assert client.delete(f"/api/appointments/{second['id']}").status_code == 204
    assert client.delete(f"/api/appointments/{second['id']}").status_code == 404
    assert len(client.get("/api/appointments").json()) == 1


def test_today_stats_use_backend_local_date(client):
    from datetime import datetime
    today_at_ten = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
    response = client.post("/api/appointments", json={
        "patient_name": "Riley Parker", "appointment_datetime": today_at_ten,
        "doctor": "Dr. Olivia Martin", "appointment_type": "Routine Check-up", "status": "Scheduled",
    })
    assert response.status_code == 201
    assert client.get("/api/appointments/stats/summary").json()["today"] == 1


def test_summary_counts_each_status(client, payload):
    create(client, payload)
    create(client, payload, patient_name="Jamie Taylor", appointment_datetime="2030-06-15T11:00:00", status="Completed")
    create(client, payload, patient_name="Jordan Lee", appointment_datetime="2030-06-15T12:00:00", status="Cancelled")
    assert client.get("/api/appointments/stats/summary").json() == {
        "total": 3, "scheduled": 1, "completed": 1, "cancelled": 1, "today": 0,
    }
