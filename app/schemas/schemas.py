from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.models import AppointmentStatus


class UserRegister(BaseModel):
    username: str
    password: str
    role_id: Optional[int] = 1

class UserOut(BaseModel):
    id: int
    username: str
    enabled: bool
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str


class PatientCreate(BaseModel):
    full_name: str
    birth_date: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class PatientOut(PatientCreate):
    id: int
    model_config = {"from_attributes": True}


class DoctorCreate(BaseModel):
    full_name: str
    specialty: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    experience_years: Optional[int] = None

class DoctorOut(DoctorCreate):
    id: int
    model_config = {"from_attributes": True}


class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None

class ServiceOut(ServiceCreate):
    id: int
    model_config = {"from_attributes": True}


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    service_id: int
    appointment_date: str
    status: Optional[AppointmentStatus] = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None

class AppointmentOut(AppointmentCreate):
    id: int
    model_config = {"from_attributes": True}
