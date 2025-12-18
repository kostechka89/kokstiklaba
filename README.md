# Auth MVP (React + FastAPI + Postgres)

Минимальный продукт для регистрации пользователей: фронтенд на React/TypeScript, бэкенд на FastAPI, база PostgreSQL, разворачивается через Docker Compose.

## Требования
- Node.js 20+
- Python 3.12+
- Docker + Docker Compose

## Быстрый старт через Docker
1. Скопируйте переменные окружения:
   ```bash
   cp .env.example .env
   ```
2. Запустите стэк:
   ```bash
   docker compose up --build
   ```
3. Откройте фронтенд на [http://localhost:5173](http://localhost:5173). Форма отправляет запросы на бэкенд `POST /api/register`.
4. Документация API доступна на [http://localhost:8000/docs](http://localhost:8000/docs).

## Локальный запуск без Docker
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env  # укажите DATABASE_URL на ваш Postgres
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host --port 5173
```

## Структура проекта
- `backend/` — FastAPI приложение, Alembic миграции, pytest тесты.
- `frontend/` — Vite + React + TypeScript SPA с формой регистрации.
- `docker-compose.yml` — сервисы `frontend`, `backend`, `db` (PostgreSQL).
- `.env.example` — пример конфигурации.

## Безопасность: что сделано
- Пароли никогда не сохраняются в открытом виде; хэширование через Argon2id (настраиваемые параметры).
- Уникальный индекс и обработка `409 Conflict` при попытке зарегистрировать дублирующий логин.
- Валидация логина/пароля на бэкенде (длина, допустимые символы, требования к сложности пароля).
- Логирование не содержит сырого пароля; фиксируются только результаты операций.
- Конфигурация вынесена в переменные окружения (`SECRET_KEY`, `DATABASE_URL`, Argon2 cost-параметры).

## Curl-примеры
```bash
# Успешная регистрация
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"login":"demo_user","password":"StrongPass1!"}'

# Конфликт логина
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"login":"demo_user","password":"AnotherPass1!"}'

# Проверка состояния сервиса
curl http://localhost:8000/healthz
```

## Тесты
```bash
cd backend
pytest
```

## Ветки и зоны ответственности
- **backend**: FastAPI, PostgreSQL, Alembic, pytest (регистрация пользователей).
- **frontend**: React/Vite, форма регистрации, обработка ответов API.
- **db**: PostgreSQL контейнер, миграции Alembic.

