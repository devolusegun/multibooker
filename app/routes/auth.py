from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.utils.auth import hash_password
from app.utils.auth import verify_password
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.jwt import create_access_token
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.email == user.email) | (User.username == user.username)).first():
        raise HTTPException(status_code=400, detail="Email or Username already registered")

    hashed_pw = hash_password(user.password)
    new_user = User(
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        phone=user.phone,
        dob=user.dob,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(data={"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user