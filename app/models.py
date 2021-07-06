from pytz import country_names
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError(_('Superuser must have is_staff=True'))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_superuser=True'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    team = models.OneToOneField('Team', on_delete=models.CASCADE, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Team(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)
    country = models.CharField(max_length=128, choices=country_names.items())
    value = models.DecimalField(max_digits=12, decimal_places=2)

    gk_count = models.PositiveSmallIntegerField(default=3)
    def_count = models.PositiveSmallIntegerField(default=6)
    mid_count = models.PositiveSmallIntegerField(default=6)
    fwd_count = models.PositiveSmallIntegerField(default=5)

    def __str__(self):
        return '[{country}] {name}'.format(country=self.country, name=self.name)

    def add_player(self, player):
        if self.gk_count + self.def_count + self.mid_count + self.fwd_count >= settings.TEAM_TOTAL_PLAYERS:
            raise Exception(f'Team can\'t have more than {settings.TEAM_TOTAL_PLAYERS} players!')
        if self.gk_count >= settings.TEAM_GOALKEEPERS:
            raise Exception(f'Team can\'t have more than {settings.TEAM_GOALKEEPERS} goalkeepers!')
        if self.def_count >= settings.TEAM_DEFENDERS:
            raise Exception(f'Team can\'t have more than {settings.TEAM_DEFENDERS} defenders!')
        if self.mid_count >= settings.TEAM_MIDFIELDERS:
            raise Exception(f'Team can\'t have more than {settings.TEAM_MIDFIELDERS} midfielders!')
        if self.fwd_count >= settings.TEAM_FORWARDS:
            raise Exception(f'Team can\'t have more than {settings.TEAM_FORWARDS} forwards!')

        self.players.add(player)


class Player(models.Model):
    PLAYER_CATEGORIES = (
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward')
    )
    category = models.CharField(max_length=16, choices=PLAYER_CATEGORIES)
    first_name = models.CharField(_('first name'), max_length=128, blank=True)
    last_name = models.CharField(_('last name'), max_length=128, blank=True)
    country = models.CharField(max_length=128, choices=country_names.items())
    age = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='players')

    def __str__(self):
        return '[{team}] {first_name} {last_name}'.format(team=self.team, first_name=self.first_name, last_name=self.last_name)