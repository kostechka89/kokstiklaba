# News Platform API

Учебное FastAPI-приложение для публикации новостей с авторизацией, ролями, кешированием и фоновыми уведомлениями.

## Стек
- FastAPI, SQLAlchemy, Alembic
- Postgres для хранения данных
- Redis для кеша новостей, профилей пользователей и refresh-сессий
- Celery + Redis для уведомлений о новостях и еженедельного дайджеста

## Быстрый старт
1. Скопируйте настройки: `cp .env.example .env` и задайте значения переменных (включая тестовые OAuth-ключи GitHub).
2. Установите зависимости: `pip install -r requirements.txt`.
3. Запустите Postgres и Redis локально или через docker-compose.
4. Примените миграции: `alembic upgrade head`.
5. Запустите сервис: `uvicorn app.main:app --reload`.
6. Поднимите фоновые задачи (отдельные терминалы):
   - `celery -A app.services.notifications.celery_app worker --loglevel=info`
   - `celery -A app.services.notifications.celery_app beat --loglevel=info`

## Примеры запросов
- Регистрация: `POST /api/auth/register` — `{ "name": "Alice", "email": "alice@example.com", "password": "alice1234" }`
- Логин: `POST /api/auth/login` — `{ "email": "author@example.com", "password": "authorpass" }`
- Создание новости (нужен автор/админ): `POST /api/news/` — `{ "title": "FastAPI", "content": {"body": "..."} }`
- Обновление новости: `PUT /api/news/{news_id}` — передайте только изменяемые поля
- Добавление комментария: `POST /api/comments/` — `{ "news_id": "<uuid>", "text": "Great!" }`

## Дополнительно
- Логирование уведомлений сохраняется в `logs/notifications.log`
- Ролевую модель и детали авторизации см. в `docs/auth.md`
