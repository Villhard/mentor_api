#!/bin/bash

# Ждем, пока база данных будет доступна
echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "PostgreSQL started"

# Собираем статические файлы
echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

# Применяем миграции
echo "Applying database migrations..."
uv run python manage.py migrate --noinput

# Запускаем сервер
echo "Starting server..."
uv run gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 4 