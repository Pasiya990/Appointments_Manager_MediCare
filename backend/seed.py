"""Insert fictional appointments into an existing user's workspace once."""
import argparse
from datetime import datetime, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Appointment, User

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--username", required=True, help="Existing MediCare account that should own the sample records")
args = parser.parse_args()

Base.metadata.create_all(bind=engine)
session = SessionLocal()
try:
    user = session.query(User).filter_by(username=args.username).first()
    if user is None:
        raise SystemExit(f"No account named {args.username!r}. Register that account in MediCare first.")

    samples = [
        Appointment(user_id=user.id, patient_name="Alex Morgan", appointment_datetime=datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) - timedelta(days=2), doctor="Dr. Emily Carter", appointment_type="General Consultation", status="Completed"),
        Appointment(user_id=user.id, patient_name="Jamie Taylor", appointment_datetime=datetime.now().replace(hour=11, minute=0, second=0, microsecond=0) + timedelta(days=1), doctor="Dr. James Wilson", appointment_type="Follow-up", status="Scheduled"),
        Appointment(user_id=user.id, patient_name="Jordan Lee", appointment_datetime=datetime.now().replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=2), doctor="Dr. Sophia Anderson", appointment_type="Dental Consultation", status="Cancelled"),
    ]
    for sample in samples:
        exists = session.query(Appointment).filter_by(user_id=user.id, patient_name=sample.patient_name).first()
        if not exists:
            session.add(sample)
    session.commit()
    print(f"Fictional sample appointments loaded for {user.username} (existing names were skipped).")
finally:
    session.close()
