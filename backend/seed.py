"""Insert a small fictional demo dataset once; safe to run more than once."""
from datetime import datetime, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Appointment

Base.metadata.create_all(bind=engine)
session = SessionLocal()
samples = [
    Appointment(patient_name="Alex Morgan", appointment_datetime=datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) - timedelta(days=2), doctor="Dr. Emily Carter", appointment_type="General Consultation", status="Completed"),
    Appointment(patient_name="Jamie Taylor", appointment_datetime=datetime.now().replace(hour=11, minute=0, second=0, microsecond=0) + timedelta(days=1), doctor="Dr. James Wilson", appointment_type="Follow-up", status="Scheduled"),
    Appointment(patient_name="Jordan Lee", appointment_datetime=datetime.now().replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=2), doctor="Dr. Sophia Anderson", appointment_type="Dental Consultation", status="Cancelled"),
]
try:
    for sample in samples:
        exists = session.query(Appointment).filter_by(patient_name=sample.patient_name).first()
        if not exists:
            session.add(sample)
    session.commit()
finally:
    session.close()
print("Fictional sample appointments loaded (existing names were skipped).")
