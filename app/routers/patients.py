from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Patient, User
from app.schemas.schemas import PatientCreate, PatientOut
from app.services.auth import get_current_user
from app.services.telegram import log_error
import openpyxl, io, logging

router = APIRouter(prefix="/patients", tags=["Пациенты"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[PatientOut], summary="Список всех пациентов")
def get_patients(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Patient).all()


@router.get("/export", summary="Экспорт пациентов в Excel")
def export_patients(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patients = db.query(Patient).all()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Пациенты"
    ws.append(["ID", "ФИО", "Дата рождения", "Телефон", "Email", "Адрес"])
    for p in patients:
        ws.append([p.id, p.full_name, p.birth_date, p.phone, p.email, p.address])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=patients.xlsx"})


@router.get("/{patient_id}", response_model=PatientOut, summary="Получить пациента по ID")
def get_patient(patient_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return p


@router.post("/", response_model=PatientOut, status_code=201, summary="Создать пациента")
def create_patient(data: PatientCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        p = Patient(**data.model_dump())
        db.add(p)
        db.commit()
        db.refresh(p)
        logger.info(f"Создан пациент: {p.full_name}")
        return p
    except Exception as e:
        log_error(f"Ошибка создания пациента: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.put("/{patient_id}", response_model=PatientOut, summary="Обновить пациента")
def update_patient(patient_id: int, data: PatientCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    for k, v in data.model_dump().items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{patient_id}", summary="Удалить пациента")
def delete_patient(patient_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    db.delete(p)
    db.commit()
    return {"message": "Пациент удалён"}
