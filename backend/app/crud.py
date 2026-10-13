from datetime import date, datetime, time, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .models import Appointment
from .schemas import AppointmentCreate, AppointmentUpdate


ACTIVE_STATUSES = ("Scheduled",)


def find_conflict(db: Session, doctor: str, starts_at: datetime, exclude_id: int | None = None):
    ends_at = starts_at + timedelta(minutes=30)
    # Doctor availability is shared across accounts; intervals are half-open.
    statement = select(Appointment).where(
        Appointment.doctor == doctor,
        Appointment.status.in_(ACTIVE_STATUSES),
        Appointment.appointment_datetime < ends_at,
        Appointment.appointment_datetime > starts_at - timedelta(minutes=30),
    )
    if exclude_id is not None:
        statement = statement.where(Appointment.id != exclude_id)
    return db.scalar(statement.limit(1))


def create_appointment(db: Session, user_id: int, data: AppointmentCreate):
    appointment = Appointment(user_id=user_id, **data.model_dump())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def update_appointment(db: Session, appointment: Appointment, data: AppointmentUpdate):
    for field, value in data.model_dump().items():
        setattr(appointment, field, value)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointment(db: Session, user_id: int, appointment_id: int):
    return db.scalar(select(Appointment).where(Appointment.id == appointment_id, Appointment.user_id == user_id))


def list_appointments(db: Session, user_id: int, search=None, status=None, doctor=None, appointment_type=None, date_filter: date | None = None):
    statement = select(Appointment).where(Appointment.user_id == user_id)
    if search:
        term = f"%{search.strip()}%"
        statement = statement.where(or_(Appointment.patient_name.ilike(term), Appointment.doctor.ilike(term)))
    if status:
        statement = statement.where(Appointment.status == status)
    if doctor:
        statement = statement.where(Appointment.doctor == doctor)
    if appointment_type:
        statement = statement.where(Appointment.appointment_type == appointment_type)
    if date_filter:
        day_start = datetime.combine(date_filter, time.min)
        day_end = day_start + timedelta(days=1)
        statement = statement.where(Appointment.appointment_datetime >= day_start, Appointment.appointment_datetime < day_end)
    return list(db.scalars(statement.order_by(Appointment.appointment_datetime, Appointment.id)))


def get_stats(db: Session, user_id: int):
    today = date.today()  # Local date of the machine running the backend.
    start = datetime.combine(today, time.min)
    end = start + timedelta(days=1)
    values = db.execute(select(
        func.count(Appointment.id),
        func.count(Appointment.id).filter(Appointment.status == "Scheduled"),
        func.count(Appointment.id).filter(Appointment.status == "Completed"),
        func.count(Appointment.id).filter(Appointment.status == "Cancelled"),
        func.count(Appointment.id).filter(Appointment.appointment_datetime >= start, Appointment.appointment_datetime < end),
    ).where(Appointment.user_id == user_id)).one()
    return dict(zip(("total", "scheduled", "completed", "cancelled", "today"), values))
