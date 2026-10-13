# CarePoint — Appointment Management System

A small, local clinic appointment dashboard built for the AI Engineering Intern practical assessment. It demonstrates CRUD operations, a REST API, validation, SQLite persistence, basic scheduling rules, dashboard counts, automated tests, and a responsive React interface. All included names and records are fictional.

> This is a local assessment demonstration. It has no authentication and is not a production healthcare system. Do not enter real patient information. No healthcare privacy or regulatory compliance is claimed.

## Assessment objectives

The project demonstrates full-stack development, understandable code, relational persistence, REST API design, validation, error handling, automated tests, UI design, technical documentation, and responsible AI usage. The code intentionally uses a small number of direct modules rather than enterprise patterns.

## Stack and features

- **Frontend:** React 18, Vite, JavaScript, Tailwind CSS 4 (Vite plugin), Lucide React, Fetch API.
- **Backend:** Python, FastAPI, Pydantic 2, SQLAlchemy 2, Uvicorn.
- **Database:** SQLite at `backend/data/appointments.db` by default.
- **Tests:** Pytest, FastAPI TestClient, isolated in-memory SQLite test database.
- Create, list, edit, and delete appointments; search patient/doctor; combine status, doctor, type, and date filters; show database-backed statistics; show loading, error, empty, success, and validation states.
- FastAPI interactive docs at `/docs`.

## Architecture and folder structure

```text
backend/
  app/
    main.py                 FastAPI app, CORS, schema initialization
    database.py             engine, session dependency, Base
    models.py               SQLAlchemy Appointment table
    schemas.py              Pydantic request/response validation
    crud.py                 database reads, writes, filtering, statistics
    routes/appointments.py  REST endpoints and conflict checks
  tests/                    TestClient tests using a separate in-memory DB
  seed.py                   Optional fictional sample records
  requirements.txt
frontend/
  src/App.jsx               dashboard and page-level state
  src/components/           cards, filters, table, form, status, confirm dialog
  src/services/             centralized Fetch API module
  src/index.css             responsive dashboard styling
  vite.config.js
AI_USAGE.md
README.md
```

The React page calls a centralized API service. FastAPI validates request data with Pydantic, delegates SQL operations to small CRUD helpers, and persists records with SQLAlchemy in SQLite. The API returns JSON and React refreshes the appointment list and statistics.

## Data model and business rules

The `appointments` table contains an automatically generated integer `id`, trimmed `patient_name` (1–100 characters), `appointment_datetime`, `doctor`, `appointment_type`, and `status`. Date/time and doctor/status fields have useful indexes. The database does not store patient details beyond the fictional/demo name and visit details.

Doctors are restricted to Dr. Emily Carter, Dr. James Wilson, Dr. Sophia Anderson, Dr. Daniel Roberts, and Dr. Olivia Martin. Appointment types are General Consultation, Follow-up, Dental Consultation, Specialist Consultation, and Routine Check-up. Status is Scheduled, Completed, or Cancelled, with new records defaulting to Scheduled.

A booking lasts 30 minutes. Only Scheduled appointments block a doctor’s schedule; Completed and Cancelled appointments do not. Intervals are half-open, so a booking at 10:30 may follow a 10:00 booking, while one at 10:15 conflicts. Update checks exclude the record being edited. Historical appointments are allowed.

Date/time inputs and filters use the local timezone of the browser/backend machine. The browser submits local ISO-style wall time; the backend SQLite `DateTime` values are treated as local wall time. “Today” in the stats response means the date on the backend host. Keep those machines’ local timezone aligned for predictable display and filtering. The 30-minute length is fixed for this assessment.

## API

All application endpoints use `/api`.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/appointments` | Validate and create; returns 201; 409 if a schedule conflict exists |
| `GET` | `/api/appointments` | List and combine optional `search`, `status`, `doctor`, `appointment_type`, and `date=YYYY-MM-DD` filters |
| `GET` | `/api/appointments/{id}` | Get one appointment or 404 |
| `PUT` | `/api/appointments/{id}` | Fully validate and update an existing appointment; 404 or 409 where appropriate |
| `DELETE` | `/api/appointments/{id}` | Delete and return 204, or 404 |
| `GET` | `/api/appointments/stats/summary` | Database-derived total, scheduled, completed, cancelled, and today counts |
| `GET` | `/api/health` | Basic API health response |

Pydantic errors return 422, missing IDs return 404, schedule conflicts return 409. The frontend displays returned errors without exposing stack traces. CORS is configured for Vite at `localhost:5173` and `127.0.0.1:5173`.

## Prerequisites

For macOS, install Python 3.11 or later, Node.js 20 or later, and npm. The implementation was built with Python 3.14.0 and Node 22.16.0 in the development environment.

## Run locally

Open two Terminal tabs from the repository root.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The default database directory and SQLite file are created automatically when the API starts. The database is persistent across API restarts. To override the DB path, export `DATABASE_URL` before starting the backend, for example `export DATABASE_URL='sqlite:///./data/appointments.db'` from `backend/`. `backend/.env.example` documents the optional setting; environment files are not loaded automatically.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # Optional; the same local API URL is the default.
npm run dev
```

Vite prints the local frontend URL, normally <http://localhost:5173>. The API is <http://localhost:8000> and interactive documentation is <http://localhost:8000/docs>. To configure another API base URL, set `VITE_API_BASE_URL` in `frontend/.env` and restart Vite.

### Optional sample records

With the backend environment installed, run:

```bash
cd backend
.venv/bin/python seed.py
```

The script uses fictional names and skips an existing record with the same patient name. It can be run more than once without repeatedly inserting its sample identities. The application works with an empty database too.

## Automated tests and production build

```bash
cd backend
.venv/bin/python -m pytest -q
```

Tests override the API DB dependency with a separate in-memory SQLite database; they do not touch `backend/data/appointments.db`. The observed run during implementation was **6 passed**. A Starlette/httpx deprecation warning may appear from the installed TestClient dependency versions.

```bash
cd frontend
npm run build
```

The observed Vite production build succeeded. Build artifacts are written to ignored `frontend/dist/`.

## Manual testing checklist

These are steps to perform; they are not claimed as already completed:

1. Start the backend and frontend using the commands above; expect API docs and dashboard to load.
2. Create an appointment with all fields; expect a success message and a new row.
3. Refresh the browser; expect the record to remain because it is in SQLite.
4. Search by patient name and doctor name; expect matching rows from the API.
5. Filter by status, doctor, type, and date individually; expect matching records.
6. Combine search and multiple filters; expect all conditions to apply together.
7. Edit a record; expect the existing record to change without creating a duplicate.
8. Create another Scheduled appointment for the same doctor 15 minutes later; expect a clear conflict error. Try a different doctor or a booking exactly 30 minutes later; expect success.
9. Change an appointment to Cancelled; expect a later overlapping booking to be accepted.
10. Delete a record and cancel a separate confirmation; expect only the confirmed deletion to remove a row.
11. Stop and restart the backend; expect prior records to remain.
12. Compare the summary cards with the rows; expect counts from database records, with today based on backend local date.
13. Use `/docs` to create and retrieve a fictional appointment; expect the documented status and response behavior.
14. Stop the backend while the page is open; expect a connection error with a retry action rather than a blank page.

## Limitations and future improvements

This assessment app has no authentication, roles, deployment setup, database migrations, pagination, concurrency locking for simultaneous bookings, or production-grade monitoring. Scheduling uses a fixed 30-minute duration and host-local wall time. Sample data is optional. Future improvements could include focused component/browser tests, database migrations, pagination, timezone-aware clinic settings, and authentication if the app were ever adapted beyond local demonstration (with appropriate privacy and security review first).

## Responsible AI usage

See [AI_USAGE.md](AI_USAGE.md) for the AI tool used, assisted areas, a human review checklist, actual corrections recorded, and test/build results. AI-assisted code still needs developer review; passing the listed commands does not verify every workflow or make this suitable for real patient data.
