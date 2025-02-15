# Mentor API

API для организации наставничества на Django с использованием DRF и JWT аутентификации.

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

API будет доступен на [http://localhost/api/](http://localhost/api/)

## API ручки
- `POST /api/registration` — регистрация (логин, пароль, телефон, email).
- `POST /api/login` — авторизация.
- `GET /api/users/` — список пользователей (только для авторизованных).
- `GET/PUT /api/users/<id>` — данные пользователя, редактирование своего аккаунта.
  - Если ментор — список менти.
  - Если есть ментор — логин ментора.
- `POST /api/logout` — выход.

## Примечание
Для большинства ручек требуется JWT аутентификация.