from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

DoctorName = Literal[
    "Dr. Emily Carter", "Dr. James Wilson", "Dr. Sophia Anderson",
    "Dr. Daniel Roberts", "Dr. Olivia Martin",
]
AppointmentType = Literal[
    "General Consultation", "Follow-up", "Dental Consultation",
    "Specialist Consultation", "Routine Check-up",
]
AppointmentStatus = Literal["Scheduled", "Completed", "Cancelled"]


class AppointmentFields(BaseModel):
    patient_name: str = Field(min_length=1, max_length=100)
    appointment_datetime: datetime
    doctor: DoctorName
    appointment_type: AppointmentType
    status: AppointmentStatus = "Scheduled"

    @field_validator("appointment_datetime")
    @classmethod
    def normalize_datetime_to_local(cls, value: datetime) -> datetime:
        # SQLite drops timezone metadata. Convert explicit offsets to the host-local wall time first.
        if value.tzinfo is not None:
            return value.astimezone().replace(tzinfo=None)
        return value

    @field_validator("patient_name", mode="before")
    @classmethod
    def trim_patient_name(cls, value):
        if isinstance(value, str):
            value = value.strip()
        return value


class AppointmentCreate(AppointmentFields):
    pass


class AppointmentUpdate(AppointmentFields):
    pass


class AppointmentRead(AppointmentFields):
    id: int
    model_config = ConfigDict(from_attributes=True)


class AppointmentStats(BaseModel):
    total: int
    scheduled: int
    completed: int
    cancelled: int
    today: int
