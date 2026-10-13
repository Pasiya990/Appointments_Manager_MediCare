from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect

from . import models
from .database import Base, engine
from .routes.auth import router as auth_router
from .routes.appointments import router as appointments_router

Base.metadata.create_all(bind=engine)
# Preserve the existing local SQLite database from the pre-login version.
if "user_id" not in {column["name"] for column in inspect(engine).get_columns("appointments")}:
    with engine.begin() as connection:
        connection.exec_driver_sql("ALTER TABLE appointments ADD COLUMN user_id INTEGER REFERENCES users(id)")
        connection.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_appointments_user_schedule ON appointments (user_id, doctor, appointment_datetime)")

app = FastAPI(title="CarePoint Appointment Management API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.include_router(appointments_router)
app.include_router(auth_router)


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok"}
