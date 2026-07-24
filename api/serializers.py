from django.contrib.auth.models import User
from rest_framework import serializers

from .models import KBEntry


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    company_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username already Exists"
            )

        return value

    def create(self, validated_data):
        company_name = validated_data.pop("company_name")

        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data["email"],
        )

        company = user.company
        company.company_name = company_name
        company.save(update_fields=['company_name'])

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True
    )


class KBEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = KBEntry
        fields = [
            "id",
            "question",
            "answer",
            "category",
        ]


class KBQuerySerializer(serializers.Serializer):
    search = serializers.CharField(
        max_length=255,
        allow_blank=True,
        trim_whitespace=False,
    )

    def validate_search(self, value):
        search_term = value.strip()

        if not search_term:
            raise serializers.ValidationError(
                "Search field cannot be blank."
            )

        return search_term
