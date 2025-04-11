from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    username = Column(String(30), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    dob = Column(Date, nullable=False)
    password = Column(String, nullable=False)  # Hashed password
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())