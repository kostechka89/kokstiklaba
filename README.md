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
GITHUB_CLIENT_ID=Ov23liDqxPu4bjGARwC7
GITHUB_CLIENT_SECRET=6f282a5798aed4b4732fef276dbdfe8124535967
```

Запуск миграций:

```bash
alembic upgrade head
```

Запуск приложения:

```bash
uvicorn app.main:app --reload
```

### OAuth GitHub
- `GET /auth/github` — редирект на GitHub.
- `GET /auth/github/callback` — callback и установка cookie с токенами.

### Основные ручки
- `POST /auth/register` — регистрация
- `POST /auth/login` — логин
- `POST /auth/refresh` — refresh
- `POST /auth/logout` — logout
- `GET /auth/sessions` — активные сессии
- `GET /auth/me` — текущий пользователь
- `GET /news/` — список новостей
- `GET /news/{id}` — новость
- `POST /news/` — создать новость (только верифицированные)
- `PATCH /news/{id}` — обновить
- `DELETE /news/{id}` — удалить
- `GET /comments/?news_id={id}` — комментарии новости
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

## Инфраструктура (метрики и логирование)

```bash
cd backend/infra
docker compose up -d
```

- Kibana: http://localhost:5601
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

Logstash читает `logs.jsonl` из корня backend и пишет в Elasticsearch (индекс `news-api-logs`).

## Запуск Celery

```bash
cd backend
celery -A app.workers.tasks.celery_app worker --loglevel=INFO
celery -A app.workers.tasks.celery_app beat --loglevel=INFO
```

## Запуск frontend

```bash
cd frontend
npm install
npm run dev
```

В `frontend/src/api/client.js` можно поменять базовый URL API.

### Пользователи из моков
Миграция `0002_mock_data.py` добавляет пользователей с паролем `password`:
- admin@example.com
- author@example.com
- reader@example.com

## Тесты

```bash
cd backend
pytest
```

E2E:

```bash
pytest -m e2e
```

## Что реализовано по заданиям

### Лабораторная 1–2: CRUD
- Модели User/News/Comment (`backend/app/db/models.py`)
- CRUD эндпоинты (`backend/app/api`)
- Миграции + моковые данные (`backend/alembic/versions`)

### Лабораторная 3: авторизация
- JWT access/refresh, хэш паролей Argon2
- GitHub OAuth ручки `/auth/github` и `/auth/github/callback`
- Роли admin/author/reader и проверки на уровне зависимостей
- Сессии с user-agent

### Лабораторная 4: Redis
- Кэш новостей и пользователей
- Хранение refresh-сессий в Redis

### Лабораторная 5: Celery
- Фоновые задачи уведомлений + weekly digest (celery beat)

### Лабораторная 6: Frontend
- Vite + React: список новостей, страница новости, логин
- Создание/редактирование/удаление с проверками ролей

### Лабораторная 7: Метрики и логирование
- Prometheus `/metrics`
- JSON логирование запросов
- Logstash/Elasticsearch/Kibana через docker compose

### Лабораторная 8: Тесты
- 3 теста API в `backend/tests`
- Playwright e2e тест
