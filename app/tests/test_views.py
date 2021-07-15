from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from ..models import User, Team, Player, TransferList
from ..api.serializers import UserSerializer


# initialize the APIClient app
api_client = APIClient()


class UserTest(APITestCase):
    def setUp(self):
        u = User.objects.create_superuser(email='admin@mail.ru', password='password1234567')
        token, created = Token.objects.get_or_create(user=u)
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        User.objects.create_user(email='test1@mail.ru', password='password1234567')
        User.objects.create_user(email='test2@mail.ru', password='password1234567')
        User.objects.create_user(email='test3@mail.ru', password='password1234567')
        User.objects.create_user(email='test4@mail.ru', password='password1234567')

    def test_login(self):
        # e2e test
        response = api_client.post(reverse('user_login'), data={'email': 'admin@mail.ru', 'password': 'password1234567'})

        user = User.objects.get(email='admin@mail.ru')
        token, created = Token.objects.get_or_create(user=user)
        self.assertEqual(response.data['token'], token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register(self):
        # e2e test
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
        # e2e test
        response = api_client.put(reverse('user_update'),
                                   data={'email': 'test4@mail.ru',
                                         'first_name': 'new name',
                                         'last_name': 'new last name'})

        user = User.objects.get(email='test4@mail.ru')
        serializer = UserSerializer(user, many=False)
        self.assertEqual(serializer.data, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        # e2e test
        response = api_client.delete(reverse('user_delete'), data={'email': 'test4@mail.ru'})
        with self.assertRaises(ObjectDoesNotExist):
            _ = User.objects.get(email='test4@mail.ru')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_all_users(self):
        # e2e test
        response = api_client.get(reverse('users_list'))
        users = User.objects.filter(role=User.USER)
        serializer = UserSerializer(users, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TeamTest(APITestCase):
    def setUp(self):
        u = User.objects.create_superuser(email='admin@mail.ru', password='password1234567')
        token, created = Token.objects.get_or_create(user=u)
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.u1 = User.objects.create_user(email='test1@mail.ru', password='password1234567')
        self.t1 = Team.objects.generate_team(self.u1)
        self.t2 = Team.objects.generate_team()
        self.p1 = Player(category='FWD', first_name='fname', last_name='lname', country='UZ', age=18, price=1000000)
        self.p1.save()

    def test_create(self):
        # e2e test
        response = api_client.post(reverse('team_create'),
                                   data={'name': 'Dram Team',
                                         'country': 'UZ'})

        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['name'], 'Dram Team')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list(self):
        # e2e test
        response = api_client.get(reverse('team_list'))

        self.assertIsNotNone(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        # e2e test
        response = api_client.put(reverse('team_update'),
                                  data={'id': self.t1.id,
                                        'name': 'New Dram Team',
                                        'country': 'UZ'})

        self.assertEqual(response.data['name'], 'New Dram Team')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        # e2e test
        response = api_client.delete(reverse('team_delete'), data={'id': self.t1.id})
        with self.assertRaises(ObjectDoesNotExist):
            _ = Team.objects.get(id=self.t1.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_add_player(self):
        # e2e test
        # set one fwd player to transfer list so that team can have available position for fwd (last() is fwd player)
        self.t1.players.last().set_to_transfer_list(1500000)

        response = api_client.put(reverse('team_add_player'),
                                  data={'player_id': self.p1.id,
                                        'team_id': self.t1.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PlayerTest(APITestCase):
    def setUp(self):
        u = User.objects.create_superuser(email='admin@mail.ru', password='password1234567')
        token, created = Token.objects.get_or_create(user=u)
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.u1 = User.objects.create_user(email='test1@mail.ru', password='password1234567')
        self.t1 = Team.objects.generate_team(self.u1)
        self.p1 = Player(category='FWD', first_name='fname', last_name='lname', country='UZ', age=18, price=1000000)
        self.p1.save()

    def test_create(self):
        # e2e test
        response = api_client.post(reverse('player_create'),
                                   data={"first_name": "Novak",
                                         "last_name": "Djokovic",
                                         "age": 34,
                                         "price": 1000000,
                                         "country": "RS",
                                         "category": "MID"})

        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['first_name'], 'Novak')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list(self):
        # e2e test
        response = api_client.get(reverse('player_list'))

        self.assertIsNotNone(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        # e2e test
        response = api_client.put(reverse('player_update'),
                                  data={"id": self.p1.id,
                                        "first_name": "new fname",
                                        "last_name": "new lname",
                                        "age": 20,
                                        "price": 2000000,
                                        "country": "UZ",
                                        "category": "FWD"})

        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['first_name'], 'new fname')
        self.assertEqual(response.data['price'], 2000000)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        # e2e test
        response = api_client.delete(reverse('player_delete'), data={'id': self.p1.id})
        with self.assertRaises(ObjectDoesNotExist):
            _ = Player.objects.get(id=self.t1.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TransferTest(APITestCase):
    def setUp(self):
        u = User.objects.create_superuser(email='admin@mail.ru', password='password1234567')
        token, created = Token.objects.get_or_create(user=u)
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.u1 = User.objects.create_user(email='test1@mail.ru', password='password1234567')
        self.t1 = Team.objects.generate_team(self.u1)
        self.p1 = Player(category='FWD', first_name='fname', last_name='lname', country='UZ', age=18, price=1000000)
        self.p1.save()

    def test_combination(self):
        def test_set(self):
            # e2e test
            response = api_client.post(reverse('set_player_to_transfer_list'),
                                       data={"player_id": self.t1.players.last().id,
                                             "asking_price": 1200000})

            _ = api_client.post(reverse('set_player_to_transfer_list'),
                                data={"player_id": self.p1.id,
                                      "asking_price": 1300000})

            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_list(self):
            # e2e test
            response = api_client.get(reverse('transfer_list'))

            self.assertIsNotNone(response.data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_buy(self):
            # e2e test

            u = User.objects.get(email='test1@mail.ru')
            token, created = Token.objects.get_or_create(user=u)
            api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

            response = api_client.post(reverse('transfer_buy'), data={"player_id": self.p1.id})

            self.assertEqual(response.status_code, status.HTTP_200_OK)

        test_set(self)
        test_list(self)
        test_buy(self)
