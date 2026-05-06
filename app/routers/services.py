from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Service, User
from app.schemas.schemas import ServiceCreate, ServiceOut
from app.services.auth import get_current_user
from app.services.telegram import log_error
import logging

router = APIRouter(prefix="/services", tags=["Услуги"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[ServiceOut], summary="Список всех услуг")
def get_services(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Service).all()


@router.get("/{service_id}", response_model=ServiceOut, summary="Получить услугу по ID")
def get_service(service_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.query(Service).filter(Service.id == service_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    return s


@router.post("/", response_model=ServiceOut, status_code=201, summary="Создать услугу")
def create_service(data: ServiceCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        s = Service(**data.model_dump())
        db.add(s)
        db.commit()
        db.refresh(s)
        logger.info(f"Создана услуга: {s.name}")
        return s
    except Exception as e:
        log_error(f"Ошибка создания услуги: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@router.put("/{service_id}", response_model=ServiceOut, summary="Обновить услугу")
def update_service(service_id: int, data: ServiceCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.query(Service).filter(Service.id == service_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    for k, v in data.model_dump().items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/{service_id}", summary="Удалить услугу")
def delete_service(service_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.query(Service).filter(Service.id == service_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    db.delete(s)
    db.commit()
    return {"message": "Услуга удалена"}
