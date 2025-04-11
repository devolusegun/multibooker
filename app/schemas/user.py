from pydantic import BaseModel, EmailStr
from datetime import date

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    username: str
    phone: str | None = None
    dob: date
    password: str

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    username: str
    dob: date

    class Config:
        orm_mode = True
