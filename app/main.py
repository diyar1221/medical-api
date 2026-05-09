from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.database import engine
from app.models import models
from app.routers import auth, patients, doctors, services, appointments
from app.services.telegram import get_error_log
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Медицинских Услуг",
    description="REST API сервер для управления сайтом медицинских услуг. JWT-аутентификация, CRUD, экспорт отчётов, Telegram-бот.",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(services.router)
app.include_router(appointments.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Необработанная ошибка {request.url}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})


@app.get("/", tags=["Система"], summary="Главная страница")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/status", tags=["Система"], summary="Статус сервера")
def status():
    return {"status": "running", "version": "1.0.0"}


@app.get("/errors", tags=["Система"], summary="Последние ошибки")
def errors():
    return {"errors": get_error_log()}
