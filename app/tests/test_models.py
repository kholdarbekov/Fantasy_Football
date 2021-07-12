from django.test import TestCase
from ..models import User


class UserTest(TestCase):
    """ Test module for User model """

    def setUp(self):
        User.objects.create_user(email='info@mail.ru', password='password1234567')
        User.objects.create_user(email='test@mail.ru', password='password1234567')

    def test_user(self):
        usr1 = User.objects.get(email='info@mail.ru')
        usr2 = User.objects.get(email='test@mail.ru')
