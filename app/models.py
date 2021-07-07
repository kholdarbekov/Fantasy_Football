import random
from pytz import country_names
import names
from names_generator import generate_name
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


class TeamManager(models.Manager):
    def generate_team(self, user):
        countries = tuple(country_names.keys())
        team = self.model(
            name=generate_name(style='capital'),
            country=countries[random.randint(0, 249)],
            value=settings.TEAM_TOTAL_PLAYERS * settings.PLAYER_INITIAL_PRICE,
            budget=settings.TEAM_INITIAL_BUDGET
        )
        team.save()

        for _ in range(settings.TEAM_GOALKEEPERS):
            player = Player(
                category='GK',
                first_name=names.get_first_name('male'),
                last_name=names.get_last_name(),
                country=countries[random.randint(0, 249)],
                age=random.randint(18, 40),
                price=settings.PLAYER_INITIAL_PRICE
            )
            player.save()
            team.add_player(player)
            team.gk_count += 1

        for _ in range(settings.TEAM_DEFENDERS):
            player = Player(
                category='DEF',
                first_name=names.get_first_name('male'),
                last_name=names.get_last_name(),
                country=countries[random.randint(0, 249)],
                age=random.randint(18, 40),
                price=settings.PLAYER_INITIAL_PRICE
            )
            player.save()
            team.add_player(player)
            team.def_count += 1

        for _ in range(settings.TEAM_MIDFIELDERS):
            player = Player(
                category='MID',
                first_name=names.get_first_name('male'),
                last_name=names.get_last_name(),
                country=countries[random.randint(0, 249)],
                age=random.randint(18, 40),
                price=settings.PLAYER_INITIAL_PRICE
            )
            player.save()
            team.add_player(player)
            team.mid_count += 1

        for _ in range(settings.TEAM_FORWARDS):
            player = Player(
                category='FWD',
                first_name=names.get_first_name('male'),
                last_name=names.get_last_name(),
                country=countries[random.randint(0, 249)],
                age=random.randint(18, 40),
                price=settings.PLAYER_INITIAL_PRICE
            )
            player.save()
            team.add_player(player)
            team.fwd_count += 1
        team.save()
        user.team = team
        user.save()


class Team(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)
    country = models.CharField(max_length=128, choices=country_names.items())
    value = models.DecimalField(max_digits=12, decimal_places=2)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    gk_count = models.PositiveSmallIntegerField(default=0)
    def_count = models.PositiveSmallIntegerField(default=0)
    mid_count = models.PositiveSmallIntegerField(default=0)
    fwd_count = models.PositiveSmallIntegerField(default=0)

    objects = TeamManager()

    def __str__(self):
        return '[{country}] {name}'.format(country=self.country, name=self.name)

    def add_player(self, player):
        if self.gk_count + self.def_count + self.mid_count + self.fwd_count >= settings.TEAM_TOTAL_PLAYERS:
            raise Exception(f'Team can\'t have more than {settings.TEAM_TOTAL_PLAYERS} players!')
        if player.category == 'GK' and self.gk_count >= settings.TEAM_GOALKEEPERS:
            raise Exception(f'Team can\'t have more than {settings.TEAM_GOALKEEPERS} goalkeepers!')
        if player.category == 'DEF' and self.def_count >= settings.TEAM_DEFENDERS:
            raise Exception(f'Team can\'t have more than {settings.TEAM_DEFENDERS} defenders!')
        if player.category == 'MID' and self.mid_count >= settings.TEAM_MIDFIELDERS:
            raise Exception(f'Team can\'t have more than {settings.TEAM_MIDFIELDERS} midfielders!')
        if player.category == 'FWD' and self.fwd_count >= settings.TEAM_FORWARDS:
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

    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='players', blank=True, null=True)

    def __str__(self):
        return '[{team}] {first_name} {last_name}'.format(team=self.team, first_name=self.first_name, last_name=self.last_name)