from django.core.exceptions import ObjectDoesNotExist
from pytz import country_names
from rest_framework import generics, status, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..documents import TransferListDocument
from ..models import User, Team, Player, TransferList
from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer, TeamSerializer, \
    TeamUpdateSerializer, PlayerSerializer, TransferListSerializer, TeamDeleteSerializer, PlayerCreateSerializer, \
    PlayerDeleteSerializer, TeamAddPlayerSerializer
from .permissions import IsAdminRoleUser
from .renderers import Renderer


class UsersListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminRoleUser, ]

    def get_queryset(self):
        users = User.objects.filter(role=User.USER)
        return users


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        error_message = list()
        try:
            email = request.data['email']
            password = request.data['password']
            _ = request.data['first_name']
            _ = request.data['last_name']
            if not email:
                error_message.append('email may not be blank')
            if not password:
                error_message.append('password may not be blank')
        except KeyError as key:
            error_message.append('{param} is not sent'.format(param=key))
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            user = serializer.instance
            token, created = Token.objects.get_or_create(user=user)
            team = Team.objects.generate_team(user)
            return Response({'token': token.key, 'type': 'user', 'team_id': team.id}, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response(data=e.args, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminRoleUser, ]

    def update(self, request, *args, **kwargs):
        try:
            return super(UserUpdateView, self).update(request, *args, **kwargs)
        except Exception as e:
            return Response(data=e.args, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        error_message = list()
        user = None
        try:
            email = self.request.data['email']
            first_name = self.request.data['first_name']
            last_name = self.request.data['last_name']
            user = User.objects.get(email=email)
            if user.role == User.ADMIN:
                error_message.append('Can not update Admin user')
            if not first_name:
                error_message.append('first_name may noy be blank')
            if not last_name:
                error_message.append('last_name may noy be blank')
        except KeyError as key:
            error_message.append('{param} is not sent'.format(param=key))
        except ObjectDoesNotExist:
            error_message.append('User not found')
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            raise Exception(*error_message)

        return user


class UserDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminRoleUser, ]
    serializer_class = UserSerializer

    def delete(self, request, *args, **kwargs):
        try:
            return super(UserDeleteView, self).delete(request, *args, **kwargs)
        except Exception as e:
            return Response(data=e.args, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        error_message = list()
        user = None
        try:
            email = self.request.data['email']
            user = User.objects.get(email=email)
            if user.role == User.ADMIN:
                error_message.append('Can not delete admin user')
        except KeyError as key:
            error_message.append('{param} is not sent'.format(param=key))
        except ObjectDoesNotExist:
            error_message.append('User not found')
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            raise Exception(*error_message)

        return user


class UserLoginView(ObtainAuthToken):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny, ]
    renderer_classes = (Renderer,)

    def post(self, request, *args, **kwargs):
        error_message = list()
        try:
            email = request.data['email']
            password = request.data['password']
            if not email:
                error_message.append('email may not be blank')
            if not password:
                error_message.append('password may not be blank')
        except KeyError as key:
            error_message.append('{param} is not sent'.format(param=key))
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_type = 'admin' if user.role == User.ADMIN else 'user'
        team_id = None
        if user.team:
            team_id = user.team.id
        return Response({'token': token.key, 'type': user_type, 'team_id': team_id})


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):

        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class TeamListView(generics.ListAPIView):
    serializer_class = TeamUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminRoleUser, ]

    def get_queryset(self):
        teams = Team.objects.all()
        return teams


class TeamDetailView(generics.RetrieveAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        try:
            return super(TeamDetailView, self).get(request, *args, **kwargs)
        except Exception as e:
            return Response(data=e.args, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        error_message = list()
        team = None

        try:
            team_id = self.request.data['id']
            team = Team.objects.get(id=team_id)
            if self.request.user.role == User.USER:
                self_team = self.request.user.team
                if self_team:
                    if self_team.id != team.id:
                        error_message.append('Can not see other user\'s team')
                else:
                    error_message.append('User has no team')
        except KeyError:
            error_message.append('parameter id is not sent')
        except ObjectDoesNotExist:
            error_message.append('Team not found')
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            raise Exception(*error_message)

        return team


class TeamUpdateView(generics.UpdateAPIView):
    serializer_class = TeamUpdateSerializer
    permission_classes = [IsAuthenticated, ]

    def update(self, request, *args, **kwargs):
        try:
            return super(TeamUpdateView, self).update(request, *args, **kwargs)
        except Exception as e:
            return Response(data=e.args, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        error_message = list()
        team = None

        try:
            team_id = self.request.data['id']
            team = Team.objects.get(id=team_id)
            if self.request.user.role == User.USER:
                self_team = self.request.user.team
                if self_team:
                    if self_team.id != team.id:
                        error_message.append('Can not update other user\'s team')
                else:
                    error_message.append('User has no team')

            name = self.request.data['name']
            if not name:
                error_message.append('name may not be blank')

            country = self.request.data['country']
            if country:
                if isinstance(country, str):
                    # TODO: comment below if you run test
                    self.request.data['country'] = country.upper()

                if self.request.data['country'] not in country_names.keys():
                    error_message.append('"{country}" is not a valid choice'.format(country=self.request.data['country']))
            else:
                error_message.append('country may not be blank')

        except KeyError as key:
            error_message.append('parameter {param} is not sent'.format(param=key))
        except ObjectDoesNotExist:
            error_message.append('Team not found')
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            raise Exception(*error_message)

        return team


class TeamCreateView(generics.CreateAPIView):
    serializer_class = TeamUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminRoleUser]

    def post(self, request, *args, **kwargs):
        error_message = list()
        try:
            name = request.data['name']
            country = request.data['country']
            if not name:
                error_message.append('name may not be blank')
            if country:
                if isinstance(country, str):
                    # TODO: comment below if you run test
                    self.request.data['country'] = country.upper()

                if self.request.data['country'] not in country_names.keys():
                    error_message.append('"{country}" is not a valid choice'.format(country=self.request.data['country']))
            else:
                error_message.append('country may not be blank')
        except KeyError as key:
            error_message.append('{param} is not sent'.format(param=key))
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)


class TeamDeleteView(generics.DestroyAPIView):
    serializer_class = TeamDeleteSerializer
    permission_classes = [IsAuthenticated, IsAdminRoleUser]

    def delete(self, request, *args, **kwargs):
        try:
            return super(TeamDeleteView, self).delete(request, *args, **kwargs)
        except Exception as e:
            return Response(data=e.args, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        error_message = list()
        team = None
        try:
            team_id = self.request.data['id']
            team = Team.objects.get(id=team_id)
        except KeyError:
            error_message.append('parameter id is not sent')
        except ObjectDoesNotExist:
            error_message.append('Team not found')
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            raise Exception(*error_message)

        return team


class PlayerListView(generics.ListAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated, IsAdminRoleUser, ]

    def get_queryset(self):
        players = Player.objects.all()
        return players


class PlayerCreateView(generics.CreateAPIView):
    serializer_class = PlayerCreateSerializer
    permission_classes = [IsAuthenticated, IsAdminRoleUser]

    def post(self, request, *args, **kwargs):
        error_message = list()
        try:
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            country = request.data['country']
            age = int(request.data['age'])
            price = float(request.data['price'])
            category = request.data['category']

            if isinstance(first_name, str):
                if not first_name:
                    error_message.append('first_name may not be blank')
            else:
                error_message.append('first_name should be string')

            if isinstance(last_name, str):
                if not last_name:
                    error_message.append('last_name may not be blank')
            else:
                error_message.append('last_name should be string')

            if isinstance(country, str):
                # TODO: comment below if you run test
                self.request.data['country'] = country.upper()
                if self.request.data['country'] not in country_names.keys():
                    error_message.append('"{country}" is not a valid choice'.format(country=self.request.data['country']))
            else:
                error_message.append('country must be string')

            if isinstance(age, int):
                if not 18 <= age <= 40:
                    error_message.append('age should be in the range [18,40]')
            else:
                error_message.append('age must be integer')

            if isinstance(price, (float, int)):
                if price <= 0:
                    error_message.append('price should be bigger than 0')
            else:
                error_message.append('price must be number')

            if isinstance(category, str):
                # TODO: comment below if you run test
                self.request.data['category'] = category.upper()
                if self.request.data['category'] not in ('GK', 'DEF', 'MID', 'FWD'):
                    error_message.append('"{category}" is not a valid choice. Options are [GK, DEF, MID, FWD]'.format(
                        category=self.request.data['category']))
            else:
                error_message.append('category must be string. options are [GK, DEF, MID, FWD]')

        except KeyError as key:
            error_message.append('{param} is not sent'.format(param=key))
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)

        return super(PlayerCreateView, self).post(request, *args, **kwargs)


class PlayerDelete(generics.DestroyAPIView):
    serializer_class = PlayerDeleteSerializer
    permission_classes = [IsAuthenticated, IsAdminRoleUser]

    def delete(self, request, *args, **kwargs):
        try:
            return super(PlayerDelete, self).delete(request, *args, **kwargs)
        except Exception as e:
            return Response(data=e.args, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        error_message = list()
        player = None
        try:
            player_id = self.request.data['id']
            player = Player.objects.get(id=player_id)
        except KeyError as key:
            error_message.append('{param} is not sent'.format(param=key))
        except ObjectDoesNotExist:
            error_message.append('Player not found')
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            raise Exception(*error_message)

        return player


class PlayerUpdateView(generics.UpdateAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated, ]

    def update(self, request, *args, **kwargs):
        try:
            return super(PlayerUpdateView, self).update(request, *args, **kwargs)
        except Exception as e:
            return Response(data=e.args, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        error_message = list()
        player = None

        try:
            player_id = self.request.data['id']
            player = Player.objects.get(id=player_id)
            age = int(self.request.data['age'])
            price = float(self.request.data['price'])
            category = self.request.data['category']

            if isinstance(age, int):
                if not 18 <= age <= 40:
                    error_message.append('age should be in the range [18,40]')
            else:
                error_message.append('age must be integer')

            if isinstance(price, (float, int)):
                if price <= 0:
                    error_message.append('price should be bigger than 0')
            else:
                error_message.append('price must be number')

            if isinstance(category, str):
                # TODO: comment below if you run test
                self.request.data['category'] = category.upper()

                if self.request.data['category'] not in ('GK', 'DEF', 'MID', 'FWD'):
                    error_message.append('"{category}" is not a valid choice. Options are [GK, DEF, MID, FWD]'.format(
                        category=self.request.data['category']))
            else:
                error_message.append('category must be string. options are [GK, DEF, MID, FWD]')

        except KeyError as key:
            error_message.append('{param} is not sent'.format(param=key))
        except ObjectDoesNotExist:
            error_message.append('Player not found')
        except Exception as e:
            error_message.extend(e.args)

        if self.request.user.role == User.USER:
            self_team = self.request.user.team
            if self_team:
                if player not in self_team.players.all():
                    error_message.append('Player not found in your team')
            else:
                error_message.append('User has no team')

        if error_message:
            raise Exception(*error_message)

        return player


class SetPlayerToTransferList(views.APIView):

    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        error_message = list()
        asking_price = -1
        player = None

        try:
            player_id = request.data['player_id']
            asking_price = request.data['asking_price']
            
            if isinstance(asking_price, (float, int)):
                if asking_price <= 0:
                    error_message.append('asking_price should be bigger than 0')
            else:
                error_message.append('asking_price must be number')

            player = Player.objects.get(id=player_id)
            if request.user.role == User.USER:
                self_team = request.user.team
                if self_team:
                    if player.team:
                        if player.team.id != self_team.id:
                            error_message.append('Player not found in your team')
                    else:
                        error_message.append('Player not found in your team')
                else:
                    error_message.append('User has no teem')

        except KeyError as key:
            error_message.append('{param} is not sent'.format(param=key))
        except ObjectDoesNotExist:
            error_message.append('Player not found')
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)

        try:
            player.set_to_transfer_list(asking_price=asking_price)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            error_message.extend(e.args)

        return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)


class TransferListView(generics.ListAPIView):
    serializer_class = TransferListSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        error_message = list()
        try:
            if request.data:
                allowed_params = (
                    'asking_price', 'player__country', 'player__name', 'player__team__name', 'player__age',
                    'player__category')
                m = map(lambda x: x in request.data, allowed_params)
                m2 = map(lambda x: x in allowed_params, request.data)
                if any(m) and all(m2):
                    return super(TransferListView, self).get(request, *args, **kwargs)
                else:
                    error_message.append('wrong param is sent')
            else:
                return super(TransferListView, self).get(request, *args, **kwargs)
        except Exception as e:
            error_message.extend(e.args)

        return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        transfers = None
        if self.request.data:
            # elasticsearch
            s = TransferListDocument.search()
            for key, value in self.request.data.items():
                s = s.query("match", **{key: value})
            # search_result = TransferListDocument.search().filter('match', **self.request.data)
            # transfers = search_result.to_queryset()
            transfers = s.to_queryset()
        else:
            transfers = TransferList.objects.all()
        return transfers


class BuyTransferView(views.APIView):
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        error_message = list()
        player = None
        buying_team = request.user.team

        if not buying_team:
            error_message.append('User has no team')

        try:
            player_id = request.data['player_id']
            player = Player.objects.get(id=player_id)
        except KeyError as key:
            error_message.append('{param} is not sent'.format(param=key))
        except ObjectDoesNotExist:
            error_message.append('Player not found')
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)

        transfer_offer = player.transfer_offer
        if transfer_offer:
            try:
                transfer_offer.make_transfer(buying_team)
                return Response(status=status.HTTP_200_OK)
            except Exception as ex:
                error_message.extend(ex.args)
        else:
            error_message.append('This player is not on Transfer list')

        return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)


class TeamAddPlayerView(generics.UpdateAPIView):
    serializer_class = TeamAddPlayerSerializer
    permission_classes = [IsAuthenticated, IsAdminRoleUser, ]

    def update(self, request, *args, **kwargs):
        try:
            return super(TeamAddPlayerView, self).update(request, *args, **kwargs)
        except Exception as e:
            return Response(data=e.args, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        error_message = list()
        team = None

        try:
            _ = self.request.data['player_id']
            team_id = self.request.data['team_id']
            team = Team.objects.get(id=team_id)
        except KeyError as key:
            error_message.append('{param} is not sent'.format(param=key))
        except ObjectDoesNotExist:
            error_message.append('Team not found')
        except Exception as e:
            error_message.extend(e.args)

        if error_message:
            raise Exception(*error_message)

        return team
