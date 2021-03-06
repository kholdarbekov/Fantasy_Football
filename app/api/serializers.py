from decimal import Decimal

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, fields
from rest_framework.exceptions import ValidationError

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
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

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
    price = serializers.DecimalField(decimal_places=2, max_digits=12, default=0, coerce_to_string=False, validators=[MinValueValidator(Decimal('0'))])

    def update(self, instance, validated_data):
        instance = super(PlayerSerializer, self).update(instance, validated_data)
        if instance.team:
            instance.team.recalculate_team_value(defer_save=False)

        return instance

    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'age', 'price', 'country', 'category']


class PlayerCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    price = serializers.DecimalField(decimal_places=2, max_digits=12, default=0, coerce_to_string=False, validators=[MinValueValidator(Decimal('0'))])

    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'age', 'price', 'country', 'category']


class PlayerDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ['id', ]


class TeamSerializer(serializers.ModelSerializer):
    value = serializers.DecimalField(read_only=True, decimal_places=2, min_value=0, max_digits=12, coerce_to_string=False, validators=[MinValueValidator(Decimal('0'))])
    budget = serializers.DecimalField(read_only=True, decimal_places=2, min_value=0, max_digits=12, coerce_to_string=False, validators=[MinValueValidator(Decimal('0'))])
    players = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'country', 'value', 'budget', 'players']


class TeamUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    value = serializers.DecimalField(decimal_places=2, min_value=0, max_digits=12, coerce_to_string=False, validators=[MinValueValidator(Decimal('0'))])
    budget = serializers.DecimalField(decimal_places=2, min_value=0, max_digits=12, coerce_to_string=False, validators=[MinValueValidator(Decimal('0'))])
    owner = serializers.StringRelatedField(many=False, read_only=True)

    def create(self, validated_data):
        team = Team.objects.generate_team(
            name=validated_data['name'],
            country=validated_data['country']
        )
        return team

    class Meta:
        model = Team
        fields = ['id', 'name', 'country', 'value', 'budget', 'owner']


class TeamDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['id', ]


class TransferListSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(many=False, read_only=True)
    asking_price = serializers.DecimalField(decimal_places=2, min_value=0, max_digits=12, coerce_to_string=False, validators=[MinValueValidator(Decimal('0'))])

    class Meta:
        model = TransferList
        fields = ['player', 'asking_price']


class TeamAddPlayerSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        player = None
        try:
            player_id = validated_data['player_id']
            player = Player.objects.get(id=player_id)
            if player.team:
                msg = _('Can not add. Player is already in a team')
                raise serializers.ValidationError(str(msg))
            instance.add_player(player)
        except ObjectDoesNotExist:
            msg = _('Player not found')
            raise serializers.ValidationError(str(msg))
        except Exception as e:
            msg = _(str(*e.args))
            raise serializers.ValidationError(str(msg))

        return player

    team_id = serializers.CharField(
        label=_("Team id"),
        style={'input_type': 'number'},
        write_only=True
    )
    player_id = serializers.CharField(
        label=_("Player id"),
        style={'input_type': 'number'},
        write_only=True
    )
    player = PlayerSerializer(many=False, read_only=True)

    def validate(self, attrs):
        team_id = attrs.get('team_id')
        player_id = attrs.get('player_id')

        if not (team_id and player_id):
            msg = _('Must include "team_id" and "player_id"')
            raise serializers.ValidationError(str(msg), code='invalid')

        return attrs
