from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length= 150)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    company_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()

    def validate_username(self,value):
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