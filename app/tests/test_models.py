from decimal import Decimal

from django.test import TestCase
from ..models import User, Team, Player, TransferList, TransferHistory


class UserTest(TestCase):
    """ Test module for User model """

    def setUp(self):
        User.objects.create_user(email='test1@mail.ru', password='password1234567')
        User.objects.create_user(email='test2@mail.ru', password='password1234567')

    def test_user_get(self):
        # unit test
        usr1 = User.objects.get(email='test1@mail.ru')
        self.assertEqual(usr1.role, User.USER)


class TeamTest(TestCase):
    """ Test module for User model """

    def setUp(self):
        self.u1 = User.objects.create_user(email='test1@mail.ru', password='password1234567')
        self.u2 = User.objects.create_user(email='test2@mail.ru', password='password1234567')

        self.t1 = Team.objects.generate_team()
        self.t2 = Team.objects.generate_team(user=self.u1)
        self.t3 = Team.objects.generate_team(name='My dream team', country='UZ')
        self.t4 = Team.objects.generate_team(user=self.u2, name='My second dream team', country='UZ')
        self.t5 = Team.objects.create(name='My Empty Team', country='US', budget=5000000, value=0)

    def test_recalculate_value(self):
        # unit test
        for player in self.t1.players.all():
            player.price = Decimal(0.2) * player.price
            player.save()

        team_value = round(self.t1.value * Decimal(0.2), 2)
        self.t1.recalculate_team_value()

        self.assertEqual(team_value, self.t1.value)

    def test_add_player(self):
        # unit test
        p1 = Player.objects.create(first_name='fname', last_name='lname', category='FWD', country='US', age=26, price=1000000)
        self.t5.add_player(p1)
        with self.assertRaises(Exception):
            self.t1.add_player(p1)


class PlayerTest(TestCase):
    pass
