from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..schemas import AppointmentCreate, AppointmentRead, AppointmentStats, AppointmentUpdate

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


def ensure_no_conflict(db: Session, doctor: str, starts_at, appointment_status: str, exclude_id: int | None = None):
    if appointment_status == "Scheduled" and crud.find_conflict(db, doctor, starts_at, exclude_id):
        raise HTTPException(status_code=409, detail="This doctor already has an active appointment within that 30-minute time slot.")


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    ensure_no_conflict(db, data.doctor, data.appointment_datetime, data.status)
    return crud.create_appointment(db, data)


@router.get("/stats/summary", response_model=AppointmentStats)
def appointment_summary(db: Session = Depends(get_db)):
    return crud.get_stats(db)


@router.get("", response_model=list[AppointmentRead])
def list_appointments(
    search: str | None = Query(default=None, max_length=100),
    status_filter: str | None = Query(default=None, alias="status"),
    doctor: str | None = Query(default=None),
    appointment_type: str | None = Query(default=None),
    date_filter: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
):
    return crud.list_appointments(db, search, status_filter, doctor, appointment_type, date_filter)


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentRead)
def update_appointment(appointment_id: int, data: AppointmentUpdate, db: Session = Depends(get_db)):
    appointment = crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    ensure_no_conflict(db, data.doctor, data.appointment_datetime, data.status, appointment_id)
    return crud.update_appointment(db, appointment, data)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    db.delete(appointment)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
