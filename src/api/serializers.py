from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "email", "phone_number"]

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

    def get_is_mentor(self, user):
        return user.is_mentor


class UserDetailSerializer(serializers.ModelSerializer):
    mentor = serializers.SerializerMethodField()
    mentees = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "password",
            "mentor",
            "mentees",
        ]

    def get_mentor(self, user):
        if user.is_mentor:
            return user.mentor.username
        return None

    def get_mentees(self, user):
        if user.mentees.exists():
            return [mentee.username for mentee in user.mentees.all()]
        return []
