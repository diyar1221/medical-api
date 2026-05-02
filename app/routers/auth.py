from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Role
from app.schemas.schemas import UserRegister, UserOut, Token
from app.services.auth import hash_password, verify_password, create_access_token
import logging

router = APIRouter(prefix="/auth", tags=["Аутентификация"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserOut, summary="Регистрация пользователя")
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    role = db.query(Role).filter(Role.title == "user").first()
    if not role:
        role = Role(title="user")
        db.add(role)
        db.flush()
    user = User(username=data.username, password=hash_password(data.password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Новый пользователь зарегистрирован: {user.username}")
    return user


@router.post("/login", summary="Вход в систему")
def login(data: UserRegister, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    token = create_access_token({"sub": user.username})
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=3600)
    logger.info(f"Пользователь вошёл: {user.username}")
    return {"message": "Успешный вход", "access_token": token}


@router.post("/logout", summary="Выход из системы")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Вы вышли из системы"}
