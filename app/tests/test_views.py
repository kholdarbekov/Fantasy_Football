from rest_framework import status
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from ..models import User
from ..api.serializers import UserSerializer, UserLoginSerializer


# initialize the APIClient app
api_client = APIClient()


class UserTest(APITestCase):
    def setUp(self):
        u = User.objects.create_superuser(email='admin@mail.ru', password='password1234567')
        User.objects.create_user(email='test1@mail.ru', password='password1234567')
        User.objects.create_user(email='test2@mail.ru', password='password1234567')
        User.objects.create_user(email='test3@mail.ru', password='password1234567')
        User.objects.create_user(email='test4@mail.ru', password='password1234567')

        token, created = Token.objects.get_or_create(user=u)
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_login(self):
        # unit test
        response = api_client.post(reverse('user_login'), data={'email': 'admin@mail.ru', 'password': 'password1234567'})

        user = User.objects.get(email='admin@mail.ru')
        token, created = Token.objects.get_or_create(user=user)
        self.assertEqual(response.data['token'], token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register(self):
        # unit test
        response = api_client.post(reverse('user_register'),
                                   data={'email': 'test5@mail.ru',
                                         'password': 'password1234567',
                                         'first_name': 'fname',
                                         'last_name': 'lname'})

        user = User.objects.get(email='test5@mail.ru')
        self.assertIsNotNone(response.data['token'])
        self.assertIsNotNone(user.team)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update(self):
        # unit test
        pass

    def test_delete(self):
        # unit test
        pass

    def test_get_all_users(self):
        # unit test
        response = api_client.get(reverse('users_list'))
        users = User.objects.filter(role=User.USER)
        serializer = UserSerializer(users, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
