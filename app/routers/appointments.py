from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Appointment, User
from app.schemas.schemas import AppointmentCreate, AppointmentOut
from app.services.auth import get_current_user
from app.services.telegram import log_error
from typing import Optional
import logging

router = APIRouter(prefix="/appointments", tags=["Записи на приём"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[AppointmentOut], summary="Список записей")
def get_appointments(patient_id: Optional[int] = None, doctor_id: Optional[int] = None,
                     db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Appointment)
    if patient_id:
        q = q.filter(Appointment.patient_id == patient_id)
    if doctor_id:
        q = q.filter(Appointment.doctor_id == doctor_id)
    return q.all()


@router.get("/{appointment_id}", response_model=AppointmentOut, summary="Получить запись по ID")
def get_appointment(appointment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    a = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return a


@router.post("/", response_model=AppointmentOut, status_code=201, summary="Создать запись")
def create_appointment(data: AppointmentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        a = Appointment(**data.model_dump())
        db.add(a)
        db.commit()
        db.refresh(a)
        logger.info(f"Создана запись на приём ID={a.id}")
        return a
    except Exception as e:
        log_error(f"Ошибка создания записи: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.put("/{appointment_id}", response_model=AppointmentOut, summary="Обновить запись")
def update_appointment(appointment_id: int, data: AppointmentCreate,
                       db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    a = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    for k, v in data.model_dump().items():
        setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return a


@router.delete("/{appointment_id}", summary="Удалить запись")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    a = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    db.delete(a)
    db.commit()
    return {"message": "Запись удалена"}
