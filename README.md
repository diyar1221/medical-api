# API Медицинских Услуг

REST API сервер для управления сайтом медицинских услуг.  
Написан на **Python + FastAPI**, MySQL, JWT-аутентификация, Telegram-бот для отслеживания ошибок.

## Возможности

- Полный CRUD для: **Пациентов**, **Врачей**, **Услуг**, **Записей на приём**
- JWT-аутентификация через cookies (регистрация, вход, выход)
- Swagger документация — автоматически на `/docs`
- Веб-интерфейс с HTML-страницами
- Экспорт данных в Excel
- Telegram-бот для уведомлений об ошибках в реальном времени
- Полное логирование всех операций

## Требования

- Python 3.10+
- MySQL 8+

## Установка

### 1. Установить зависимости

```bash
pip install -r requirements.txt
```

### 2. База данных

Создать базу данных MySQL:
```sql
CREATE DATABASE medical_fastapi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Конфигурация

Отредактировать `app/database.py`:
```python
DATABASE_URL = "mysql+pymysql://root:пароль@localhost:3306/medical_fastapi"
```

### 4. Запуск

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Открыть в браузере: **http://localhost:8000**

## Страницы сайта

| Страница | URL |
|----------|-----|
| Вход / Регистрация | `/` |
| Пациенты | `/static/patients.html` |
| Врачи | `/static/doctors.html` |
| Услуги | `/static/services.html` |
| Записи на приём | `/static/appointments.html` |
| Swagger API | `/docs` |

## Эндпоинты API

### Аутентификация
| Метод | Путь | Описание |
|-------|------|----------|
| POST | /auth/register | Регистрация |
| POST | /auth/login | Вход (JWT в cookie) |
| POST | /auth/logout | Выход |

### Пациенты
| Метод | Путь | Описание |
|-------|------|----------|
| GET | /patients/ | Список пациентов |
| GET | /patients/{id} | Получить по ID |
| POST | /patients/ | Создать |
| PUT | /patients/{id} | Обновить |
| DELETE | /patients/{id} | Удалить |
| GET | /patients/export | Экспорт в Excel |

### Врачи, Услуги, Записи
Аналогичные эндпоинты для `/doctors/`, `/services/`, `/appointments/`

## Telegram-бот

Указать токен и chat_id в `app/services/telegram.py`.

| Команда | Описание |
|---------|----------|
| /status | Статус сервера |
| /errors | Последние 20 ошибок |

## Структура проекта

```
app/
├── main.py              — точка входа, настройка FastAPI
├── database.py          — подключение к MySQL
├── models/models.py     — SQLAlchemy модели (User, Role, Patient, Doctor, Service, Appointment)
├── schemas/schemas.py   — Pydantic схемы валидации
├── routers/             — маршруты API
│   ├── auth.py          — аутентификация
│   ├── patients.py      — пациенты
│   ├── doctors.py       — врачи
│   ├── services.py      — услуги
│   └── appointments.py  — записи на приём
└── services/
    ├── auth.py          — JWT, хэширование паролей
    └── telegram.py      — Telegram-бот
static/
├── index.html           — страница входа/регистрации
├── patients.html        — управление пациентами
├── doctors.html         — управление врачами
├── services.html        — управление услугами
└── appointments.html    — записи на приём
```
