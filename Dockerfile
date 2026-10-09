FROM python:3.14-slim

# Установить зависимости системы
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Установить uv для управления зависимостями
RUN pip install --no-cache-dir uv

# Создать рабочую директорию
WORKDIR /app

# Скопировать файлы проекта
COPY pyproject.toml ./
COPY src/ ./src/
COPY celery_worker.py ./
COPY README.md .

# Установить зависимости Python
#RUN uv sync

# Создать директорию для сессии Telethon
RUN mkdir -p /app/session

# Создать пользователя для запуска (без root)
RUN useradd -m appuser
USER appuser

# Команда по умолчанию — запуск Celery worker
CMD ["uv", "run", "python", "celery_worker.py", "worker", "--loglevel=info"]
