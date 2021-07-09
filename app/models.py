import random
from decimal import Decimal
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
        extra_fields.setdefault('role', User.ADMIN)

        if not extra_fields.get('is_staff'):
            raise ValueError(_('Superuser must have is_staff=True'))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_superuser=True'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    USER = 1
    ADMIN = 2

    ROLE_CHOICES = (
        (USER, 'Ordinary User'),
        (ADMIN, 'Admin User')
    )

    username = None
    email = models.EmailField(_('email address'), unique=True)
    team = models.OneToOneField('Team', on_delete=models.CASCADE, related_name='owner', blank=True, null=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=ROLE_CHOICES[0][0])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class TeamManager(models.Manager):
    def generate_team(self, user):
        countries = tuple(country_names.keys())
        num_of_countries = len(countries)
        team = self.model(
            name=generate_name(style='capital'),
            country=countries[random.randint(0, num_of_countries)],
            value=settings.TEAM_TOTAL_PLAYERS * settings.PLAYER_INITIAL_PRICE,
            budget=settings.TEAM_INITIAL_BUDGET
        )
        team.save()

        for _ in range(settings.TEAM_GOALKEEPERS):
            player = Player(
                category='GK',
                first_name=names.get_first_name('male'),
                last_name=names.get_last_name(),
                country=countries[random.randint(0, num_of_countries)],
                age=random.randint(18, 40),
                price=settings.PLAYER_INITIAL_PRICE
            )
            player.save()
            team.add_player(player, defer_save=True)

        for _ in range(settings.TEAM_DEFENDERS):
            player = Player(
                category='DEF',
                first_name=names.get_first_name('male'),
                last_name=names.get_last_name(),
                country=countries[random.randint(0, num_of_countries)],
                age=random.randint(18, 40),
                price=settings.PLAYER_INITIAL_PRICE
            )
            player.save()
            team.add_player(player, defer_save=True)

        for _ in range(settings.TEAM_MIDFIELDERS):
            player = Player(
                category='MID',
                first_name=names.get_first_name('male'),
                last_name=names.get_last_name(),
                country=countries[random.randint(0, num_of_countries)],
                age=random.randint(18, 40),
                price=settings.PLAYER_INITIAL_PRICE
            )
            player.save()
            team.add_player(player, defer_save=True)

        for _ in range(settings.TEAM_FORWARDS):
            player = Player(
                category='FWD',
                first_name=names.get_first_name('male'),
                last_name=names.get_last_name(),
                country=countries[random.randint(0, num_of_countries)],
                age=random.randint(18, 40),
                price=settings.PLAYER_INITIAL_PRICE
            )
            player.save()
            team.add_player(player, defer_save=True)

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

    def add_player(self, player, defer_save=False):
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

        if player.category == 'GK':
            self.gk_count += 1
        elif player.category == 'DEF':
            self.def_count += 1
        elif player.category == 'MID':
            self.mid_count += 1
        elif player.category == 'FWD':
            self.fwd_count += 1

        if not defer_save:
            self.save()

    def recalculate_team_value(self):
        total_value = 0
        for player in self.players.all():
            total_value += player.price
        self.value = total_value

    def set_player_to_transfer_list(self, player):
        if player.category == 'GK':
            self.gk_count -= 1
        elif player.category == 'DEF':
            self.def_count -= 1
        elif player.category == 'MID':
            self.mid_count -= 1
        elif player.category == 'FWD':
            self.fwd_count -= 1

        self.save()


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
        return '[{team}] {first_name} {last_name}'.format(team=self.team.name, first_name=self.first_name, last_name=self.last_name)

    def increase_price(self):
        increase_percent = (random.randint(10, 100) + 100) / 100
        self.price = Decimal(increase_percent) * self.price


class TransferList(models.Model):
    player = models.OneToOneField('Player', related_name='transfer_offer', on_delete=models.CASCADE)
    asking_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return '{player} {price}'.format(player=self.player, price=self.asking_price)

    def make_transfer(self, buying_team):
        selling_team = self.player.team

        if selling_team.id == buying_team.id:
            raise Exception('Buying team is same with selling team')

        if buying_team.budget < self.asking_price:
            raise Exception('Buying team does not have enough budget to buy this player!')
        else:
            selling_team.players.remove(self.player)
            selling_team.budget += self.asking_price
            selling_team.recalculate_team_value()
            selling_team.save()

            self.player.increase_price()
            self.player.save()
            buying_team.add_player(self.player, defer_save=True)
            buying_team.recalculate_team_value()
            buying_team.budget -= self.asking_price
            buying_team.save()

            transfer = TransferHistory(player=self.player, sell_team=selling_team, buy_team=buying_team, sell_price=self.asking_price)
            transfer.save()

            self.delete()


class TransferHistory(models.Model):
    player = models.ForeignKey('Player', related_name='transfer_history', on_delete=models.CASCADE)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    sell_team = models.ForeignKey('Team', related_name='transfer_sells_history', on_delete=models.SET_NULL, blank=True, null=True)
    buy_team = models.ForeignKey('Team', related_name='transfer_buys_history', on_delete=models.SET_NULL, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{player_fname} {player_lname}: {sell_team} -> {buy_team}'.format(
            player_fname=self.player.first_name,
            player_lname=self.player.last_name,
            sell_team=self.sell_team.name,
            buy_team=self.buy_team.name
        )
