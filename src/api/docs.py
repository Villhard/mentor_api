from drf_spectacular.utils import extend_schema


docs_schemes = {
    "registration": extend_schema(
        methods=["POST"],
        summary="Регистрация пользователя",
        tags=["auth"],
    ),
    "login": extend_schema(
        methods=["POST"],
        summary="Вход в систему",
        tags=["auth"],
    ),
    "logout": extend_schema(
        methods=["POST"],
        summary="Выход из системы",
        tags=["auth"],
    ),
    "refresh": extend_schema(
        methods=["POST"],
        summary="Обновление токена",
        tags=["auth"],
    ),
    "user_list": extend_schema(
        methods=["GET"],
        summary="Список пользователей",
        tags=["users"],
    ),
    "user_detail": extend_schema(
        methods=["GET", "PUT", "PATCH"],
        summary="Просмотр и редактирование профиля",
        tags=["users"],
    ),
}
