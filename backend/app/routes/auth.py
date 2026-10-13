from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import SESSION_COOKIE, SESSION_MAX_AGE, create_session_token, get_current_user, hash_password, verify_password
from ..database import get_db
from ..models import User
from ..schemas import AuthCredentials, UserRead

router = APIRouter(prefix="/api/auth", tags=["authentication"])


def start_session(response: Response, user: User) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=create_session_token(user.id),
        httponly=True,
        secure=False,  # Local HTTP development; enable HTTPS and secure cookies in deployment.
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/",
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: AuthCredentials, response: Response, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.username == data.username))
    if existing:
        raise HTTPException(status_code=409, detail="That username is already registered.")
    user = User(username=data.username, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    start_session(response, user)
    return user


@router.post("/login", response_model=UserRead)
def login(data: AuthCredentials, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == data.username))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username or password is incorrect.")
    start_session(response, user)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="lax")
    response.status_code = status.HTTP_204_NO_CONTENT


@router.get("/me", response_model=UserRead)
def current_user(user: User = Depends(get_current_user)):
    return user
