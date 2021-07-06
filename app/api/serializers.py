from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, fields
from ..models import User


class UserSerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField('team_name')

    def team_name(self, obj):
        return obj.team.name if obj.team else ''

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'team']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']
