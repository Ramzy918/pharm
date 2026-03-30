from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "is_active", "pharmacy_name", "wilaya")
        read_only_fields = fields


class UserRegisterSerializer(serializers.ModelSerializer):
    """Pour l'enregistrement public (password obligatoire)"""
    password = serializers.CharField(write_only=True, min_length=8, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "role", "pharmacy_name", "wilaya")

    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data.get("role", "PRO")
        user = User(**validated_data)
        if role == "PHARMACY" or user.role == "PHARMACY":
            user.is_active = False
        user.set_password(password)
        user.save()
        return user


class UserWriteSerializer(serializers.ModelSerializer):
    """Pour la modification (password optionnel)"""
    password = serializers.CharField(write_only=True, min_length=8, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "role", "is_active", "is_staff", "pharmacy_name", "wilaya")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
