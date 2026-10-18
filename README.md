# AINEWS: AI-генератор постов для Telegram

Сервис автоматического сбора новостей, генерации постов через AI и публикации в Telegram.

## Стек

- **FastAPI** — REST API
- **Celery + Redis** — асинхронные задачи
- **PostgreSQL** — база данных
- **Telethon** — Telegram API
- **OpenAI GPT-4** — генерация постов
- **SQLAlchemy** — ORM
- **BeautifulSoup4** — парсинг сайтов

## Установка

### 1. Клонирование и настройка окружения

```bash
# Установить зависимости
uv sync

# Скопировать файл окружения
cp .env.example .env
```

### 2. Заполнение `.env`

```env
POSTGRES_USER=ainews
POSTGRES_PASSWORD=ainews_pass
POSTGRES_DB=ainews

DATABASE_URL=postgresql+psycopg2://ainews:ainews_pass@localhost:5432/ainews
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_telegram_api_hash
TELEGRAM_SESSION_PATH=session
TELEGRAM_TARGET_CHANNEL=@your_target_channel
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
APP_HOST=127.0.0.1
APP_PORT=8000
```

### 3. Запуск через Docker Compose (рекомендуется)

```bash
# Запустить все сервисы (PostgreSQL, Redis, Celery worker, Celery beat, API)
docker-compose up -d

# Посмотреть логи
docker-compose logs -f api
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat

# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (удалит данные)
docker-compose down -v
```

### 4. Локальный запуск (без Docker)

#### 4.1. Запуск PostgreSQL и Redis

```bash
# PostgreSQL (Docker)
docker run --name ainews-db -e POSTGRES_USER=ainews -e POSTGRES_PASSWORD=ainews_pass -e POSTGRES_DB=ainews -p 5432:5432 -d postgres

# Redis (Docker)
docker run --name ainews-redis -p 6379:6379 -d redis
```

#### 4.2. Инициализация базы данных

```bash
uv run python -c "from pythonproject_4.db import init_db; init_db()"
```

#### 4.3. Авторизация в Telegram

```bash
uv run python -m create_session.py
# Введите номер телефона и код подтверждения
```

#### 4.4. Запуск приложения

```bash
# Терминал 1: FastAPI
uv run uvicorn pythonproject_4.main:app --reload --port 8000

# Терминал 2: Celery worker
uv run python celery_worker.py worker --loglevel=info

# Терминал 3 (опционально): Celery Beat для расписания
uv run python celery_worker.py beat --loglevel=info --schedule celerybeat-schedule
```

## API Документация

После запуска откройте:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Основные эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/sources/` | Список источников |
| POST | `/api/sources/` | Создать источник |
| GET | `/api/sources/{id}/` | Данные источника |
| PATCH | `/api/sources/{id}/` | Обновить источник |
| DELETE | `/api/sources/{id}/` | Удалить источник |
| GET | `/api/news/` | Список новостей |
| GET | `/api/posts/` | Список постов |
| GET | `/api/posts/{id}/` | Данные поста |
| POST | `/api/parse/` | Запустить сбор новостей |
| POST | `/api/generate/` | Сгенерировать пост |
| POST | `/api/posts/{id}/publish/` | Опубликовать пост |

## Структура проекта

```
├── src/pythonproject_4/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Настройки
│   ├── db.py                # База данных
│   ├── models.py            # ORM модели
│   ├── schemas.py           # Pydantic схемы
│   ├── tasks.py             # Celery задачи
│   ├── api/
│   │   └── endpoints.py     # REST endpoints
│   ├── news_parser/
│   │   ├── base.py          # Базовый парсер
│   │   ├── sites.py         # Парсеры сайтов
│   │   └── telegram.py      # Парсер Telegram
│   ├── ai/
│   │   ├── client.py        # OpenAI клиент
│   │   └── generator.py     # Генерация постов
│   └── telegram/
│       ├── client.py        # Telethon клиент
│       ├── authorize.py     # Авторизация
│       └── publisher.py     # Публикация
├── celery_worker.py         # Celery worker
├── .env.example             # Шаблон окружения
└── .gitignore
```

## Лицензия

MIT
