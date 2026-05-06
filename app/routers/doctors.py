from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Doctor, User
from app.schemas.schemas import DoctorCreate, DoctorOut
from app.services.auth import get_current_user
from app.services.telegram import log_error
import openpyxl, io, logging
from typing import Optional

router = APIRouter(prefix="/doctors", tags=["Врачи"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[DoctorOut], summary="Список всех врачей")
def get_doctors(specialty: Optional[str] = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Doctor)
    if specialty:
        q = q.filter(Doctor.specialty == specialty)
    return q.all()


@router.get("/export", summary="Экспорт врачей в Excel")
def export_doctors(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    doctors = db.query(Doctor).all()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Врачи"
    ws.append(["ID", "ФИО", "Специальность", "Телефон", "Email", "Опыт (лет)"])
    for d in doctors:
        ws.append([d.id, d.full_name, d.specialty, d.phone, d.email, d.experience_years])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=doctors.xlsx"})


@router.get("/{doctor_id}", response_model=DoctorOut, summary="Получить врача по ID")
def get_doctor(doctor_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    d = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Врач не найден")
    return d


@router.post("/", response_model=DoctorOut, status_code=201, summary="Создать врача")
def create_doctor(data: DoctorCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        d = Doctor(**data.model_dump())
        db.add(d)
        db.commit()
        db.refresh(d)
        logger.info(f"Создан врач: {d.full_name}")
        return d
    except Exception as e:
        log_error(f"Ошибка создания врача: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.put("/{doctor_id}", response_model=DoctorOut, summary="Обновить врача")
def update_doctor(doctor_id: int, data: DoctorCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    d = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Врач не найден")
    for k, v in data.model_dump().items():
        setattr(d, k, v)
    db.commit()
    db.refresh(d)
    return d


@router.delete("/{doctor_id}", summary="Удалить врача")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    d = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Врач не найден")
    db.delete(d)
    db.commit()
    return {"message": "Врач удалён"}
