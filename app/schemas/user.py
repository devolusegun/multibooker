from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    phone: str | None = None
    dob: str | None = None
    password: str
