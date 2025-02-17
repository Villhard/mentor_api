# Mentor API

API для организации наставничества на Django с использованием DRF и JWT аутентификации.

## Технологии
- Python 3.12
- Django + DRF
- PostgreSQL
- JWT аутентификация
- Docker
- Nginx
- OpenAPI (Swagger)

## Запуск
1. Склонируйте репозиторий:
   ```
   git clone https://github.com/Villhard/mentor_api.git
   ```

2. Создайте `.env` на основе `.env.example`.
   ```
   cp .env.example .env
   ```

3. Запустите контейнеры:
   ```
   docker-compose up -d
   ```

Документация API: [http://localhost/api/swagger/](http://localhost/api/swagger/)

## API Endpoints

### Аутентификация
- `POST /api/registration/` — регистрация
- `POST /api/login/` — получение JWT токена
- `POST /api/refresh/` — обновление JWT токенов
- `POST /api/logout/` — выход (блокировка токена)

### Пользователи
- `GET /api/users/` — список всех пользователей (только для авторизованных)
- `GET /api/users/{id}/` — детальная информация о пользователе
  - Для менторов: список подопечных
  - Для менти: информация о менторе
- `PUT /api/users/{id}/` — обновление своего профиля


## Документация
Полная документация API доступна через Swagger UI после запуска проекта.