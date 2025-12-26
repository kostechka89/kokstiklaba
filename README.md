# News platform (backend + frontend)

Репозиторий содержит две папки:
- `backend` — FastAPI сервис новостей.
- `frontend` — React приложение на Vite.

## Требования
- Python 3.10+
- Node.js 18+
- PostgreSQL
- Redis

## Запуск backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Создайте `.env` (пример):

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/news
SECRET_KEY=change_me
REDIS_URL=redis://localhost:6379/0
GITHUB_CLIENT_ID=mock
GITHUB_CLIENT_SECRET=mock
```

Запуск миграций:

```bash
alembic upgrade head
```

Запуск приложения:

```bash
uvicorn app.main:app --reload
```

### Основные ручки
- `POST /auth/register` — регистрация
- `POST /auth/login` — логин
- `POST /auth/refresh` — refresh
- `POST /auth/logout` — logout
- `GET /auth/sessions` — активные сессии
- `GET /news/` — список новостей
- `GET /news/{id}` — новость
- `POST /news/` — создать новость (только верифицированные)
- `PATCH /news/{id}` — обновить
- `DELETE /news/{id}` — удалить
- `POST /comments/` — создать комментарий
- `PATCH /comments/{id}` — обновить комментарий
- `DELETE /comments/{id}` — удалить комментарий

### Примеры curl

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"User","email":"user@example.com","password":"pass"}'

curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}'

curl -X GET http://localhost:8000/news/
```

## Запуск frontend

```bash
cd frontend
npm install
npm run dev
```

В `frontend/src/api/client.js` можно поменять базовый URL API.

## Тесты

```bash
cd backend
pytest
```

## Что реализовано по заданиям

### Лабораторная 1–2: CRUD
- Модели User/News/Comment (`backend/app/db/models.py`)
- CRUD эндпоинты (`backend/app/api`)
- Миграции + моковые данные (`backend/alembic/versions`)

### Лабораторная 3: авторизация
- JWT access/refresh, хэш паролей Argon2
- Роли admin/author/reader и проверки на уровне зависимостей
- Сессии с user-agent

### Лабораторная 4: Redis
- Кэш новостей и пользователей
- Хранение refresh-сессий в Redis

### Лабораторная 5: Celery
- Фоновые задачи уведомлений (логирование в файл `notifications.log`)

### Лабораторная 6: Frontend
- Vite + React: список новостей, страница новости, логин

### Лабораторная 7: Метрики и логирование
- Prometheus `/metrics`
- JSON логирование запросов

### Лабораторная 8: Тесты
- 3 теста API в `backend/tests`
