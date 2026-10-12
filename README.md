# Tasklist Backend

REST API для списка задач с регистрацией пользователей и JWT-аутентификацией. Написан на **FastAPI**, **SQLAlchemy** и **PostgreSQL**.

**Демо (Swagger UI):** https://tasklist-backend-2rbk.onrender.com/docs

## Возможности

- Регистрация и вход пользователей, JWT-токены доступа (`python-jose`), хеширование паролей через `bcrypt`
- CRUD для задач (название, признак выполнения, необязательный приоритет)
- Валидация запросов и ответов через Pydantic v2
- PostgreSQL через SQLAlchemy 2 и `psycopg 3`
- Миграции базы данных на Alembic
- Слоистая структура: routes → services → repositories
- Тесты на pytest
- Конфигурация для Docker и docker-compose

## Технологии

| Область | Инструменты |
|---------|-------------|
| Фреймворк | FastAPI, Uvicorn |
| База данных | PostgreSQL 16, SQLAlchemy 2, Alembic |
| Аутентификация | python-jose (JWT), bcrypt |
| Валидация и настройки | Pydantic, pydantic-settings, python-dotenv |
| Тестирование | pytest, httpx |
| Инфраструктура | Docker, docker-compose |

## Структура проекта

```
.
├── alembic/             # скрипты миграций
├── repositories/        # слой доступа к данным
├── routes/              # роутеры API (tasks, auth)
├── services/            # бизнес-логика
├── config.py            # настройки из переменных окружения
├── database.py          # движок и сессии БД
├── dependencies.py      # зависимости FastAPI (сессия БД, текущий пользователь)
├── models.py            # модели SQLAlchemy
├── schemas.py           # схемы Pydantic
├── security.py          # хеширование паролей, создание и проверка JWT
├── main.py              # точка входа приложения
├── tests.py, conftest.py
├── Dockerfile
├── docker-compose.yaml
├── alembic.ini
└── .env.example
```

## Настройка

Скопируй `.env.example` в `.env` и заполни значения:

```bash
cp .env.example .env
```

| Переменная | Описание | Пример |
|------------|----------|--------|
| `DATABASE_URL` | Строка подключения к PostgreSQL | `postgresql+psycopg://user:password@host:5432/dbname` |
| `SECRET_KEY` | Секрет для подписи JWT-токенов | случайная строка из 32 байт |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена доступа в минутах | `60` |

Сгенерировать секретный ключ:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Запуск

### Через Docker (рекомендуется)

```bash
docker compose up --build
```

API будет доступен на http://localhost:8000, Swagger UI на http://localhost:8000/docs.
PostgreSQL проброшен на порт `5432`.

### Локально

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# укажи в .env DATABASE_URL работающего PostgreSQL
alembic upgrade head
uvicorn main:app --reload
```

## Миграции

```bash
alembic upgrade head                              # применить миграции
alembic revision --autogenerate -m "описание"     # создать новую миграцию
alembic downgrade -1                              # откатить на один шаг
```

## API

Интерактивная документация генерируется автоматически:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

### Эндпоинты

**Аутентификация**

| Метод | Путь | Описание | Тело запроса | Ответ |
|-------|------|----------|--------------|-------|
| `POST` | `/auth/register` | Регистрация пользователя | `UserCreate` | `201`, `UserOut` |
| `POST` | `/auth/login` | Вход, получение JWT | `UserCreate` (JSON: email и password) | `200`, `TokenOut` |

**Задачи** (все эндпоинты требуют `Bearer`-токен, пользователь видит только свои задачи)

| Метод | Путь | Описание | Параметры / тело | Ответ |
|-------|------|----------|------------------|-------|
| `GET` | `/tasks` | Список задач | query: `done` (фильтр по статусу), `limit` (по умолчанию 10) | `200`, `list[Task]` |
| `GET` | `/tasks/{task_id}` | Получить задачу | — | `200`, `Task` (или 404) |
| `POST` | `/tasks` | Создать задачу | `TaskCreate` | `201`, `Task` |
| `PATCH` | `/tasks/{task_id}` | Частично обновить задачу | `TaskUpdate` | `200`, `Task` |
| `DELETE` | `/tasks/{task_id}` | Удалить задачу | — | `204` |

### Пример использования

```bash
# регистрация
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'

# вход
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'

# создание задачи
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Купить молоко"}'

# невыполненные задачи
curl "http://localhost:8000/tasks?done=false&limit=5" \
  -H "Authorization: Bearer <access_token>"
```

Авторизованные запросы передают заголовок:

```
Authorization: Bearer <access_token>
```

### Модели данных

```
TaskCreate   { title: str, done: bool = false }
Task         { id: int, title: str, done: bool, priority: int | null }
TaskUpdate   { title?: str, done?: bool }
UserCreate   { email: EmailStr, password: str }
UserOut      { id: int, email: EmailStr }
TokenOut     { access_token: str, token_type: "bearer" }
```

## Тесты

Для тестов нужна отдельная база PostgreSQL, она задаётся через `TEST_DATABASE_URL`
(в docker-compose указывает на базу `tasklist_test`):

```bash
pytest
```
