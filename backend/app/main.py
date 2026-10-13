from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import Base, engine
from .routes.appointments import router as appointments_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CarePoint Appointment Management API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.include_router(appointments_router)


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok"}
