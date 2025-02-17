import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "password", "email", "phone_number"]

    def validate_phone_number(self, value):
        phone_pattern = re.compile(r"^\+?[1-9]\d{8,14}$")
        if not phone_pattern.match(value):
            raise serializers.ValidationError("Неверный формат номера телефона")
        return value

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            phone_number=validated_data.get("phone_number", ""),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    is_mentor = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "is_mentor"]

    @extend_schema_field(bool)
    def get_is_mentor(self, user):
        return user.is_mentor


class UserDetailSerializer(serializers.ModelSerializer):
    mentor = serializers.SerializerMethodField()
    mentees = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "mentor",
            "mentees",
        ]

    @extend_schema_field(str)
    def get_mentor(self, user):
        if user.mentor:
            return user.mentor.username
        return None

    @extend_schema_field(list[str])
    def get_mentees(self, user):
        if user.mentees.exists():
            return [mentee.username for mentee in user.mentees.all()]
        return []

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for field in ["mentor", "mentees"]:
            if representation[field] in [None, []]:
                representation.pop(field)
        return representation


class UserUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    mentor = serializers.CharField(required=False, allow_null=True)
    mentees = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True
    )
    mentees_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "phone_number", "mentor", "mentees", "mentees_data", "old_password", "new_password"]

    @extend_schema_field(list[str])
    def get_mentees_data(self, obj):
        return [mentee.username for mentee in obj.mentees.all()]

    def validate(self, attrs):
        if "new_password" in attrs:
            if "old_password" not in attrs:
                raise serializers.ValidationError("Старый пароль не указан")
            if not self.instance.check_password(attrs["old_password"]):
                raise serializers.ValidationError("Старый пароль неверный")
        return attrs

    def validate_mentor(self, value):
        if value:
            try:
                return User.objects.get(username=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("Ментор не найден")
        return None

    def validate_mentees(self, values):
        if values:
            try:
                return User.objects.filter(username__in=values)
            except User.DoesNotExist:
                raise serializers.ValidationError("Менти не найдены")
        return []

    def update(self, instance, validated_data):
        if "new_password" in validated_data:
            instance.set_password(validated_data.pop("new_password"))
            validated_data.pop("old_password", None)
            instance.save()

        if "mentees" in validated_data:
            instance.mentees.set(validated_data.pop("mentees"))

        if "mentor" in validated_data:
            instance.mentor = validated_data.pop("mentor")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.mentor:
            representation['mentor'] = instance.mentor.username
        representation['mentees'] = representation.pop('mentees_data', [])

        for field in ["mentor", "mentees"]:
            if representation[field] in [None, []]:
                representation.pop(field)

        return representation