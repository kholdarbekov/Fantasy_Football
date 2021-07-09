from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, fields
from ..models import User, Team, Player, TransferList


class UserSerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField('team_name', read_only=True)
    team_id = serializers.SerializerMethodField('team_identifier', read_only=True)

    def team_name(self, obj):
        return obj.team.name if obj.team else ''

    def team_identifier(self, obj):
        return obj.team.id if obj.team else ''

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'team', 'team_id']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=User.USER
        )
        return user

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class PlayerSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    price = serializers.DecimalField(read_only=True, decimal_places=2, max_digits=12, default=0)
    category = serializers.CharField(read_only=True, max_length=16)

    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'age', 'price', 'country', 'category', 'id']


class TeamSerializer(serializers.ModelSerializer):
    value = serializers.DecimalField(read_only=True, decimal_places=2, min_value=0, max_digits=12)
    budget = serializers.DecimalField(read_only=True, decimal_places=2, min_value=0, max_digits=12)
    players = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'country', 'value', 'budget', 'players']


class TeamUpdateSerializer(serializers.ModelSerializer):
    value = serializers.DecimalField(read_only=True, decimal_places=2, min_value=0, max_digits=12)
    budget = serializers.DecimalField(read_only=True, decimal_places=2, min_value=0, max_digits=12)
    owner = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'country', 'value', 'budget', 'owner']


class TransferListSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(many=False, read_only=True)

    class Meta:
        model = TransferList
        fields = ['player', 'asking_price']
