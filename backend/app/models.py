from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointments_datetime_doctor", "appointment_datetime", "doctor"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_name: Mapped[str] = mapped_column(String(100), nullable=False)
    appointment_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    doctor: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    appointment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Scheduled", index=True)
