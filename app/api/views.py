from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..models import User, Team, Player, TransferList
from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer, TeamSerializer, \
    TeamUpdateSerializer, PlayerSerializer, TransferListSerializer
from .permissions import IsAdminRoleUser


class UsersListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminRoleUser, ]

    def get_queryset(self):
        users = User.objects.filter(role=User.USER)
        return users


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny, ]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        # TODO: validate input params
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user = serializer.instance
        token, created = Token.objects.get_or_create(user=user)

        Team.objects.generate_team(user)

        return Response({'token': token.key}, status=status.HTTP_201_CREATED, headers=headers)


class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminRoleUser, ]

    def update(self, request, *args, **kwargs):
        try:
            return super(UserUpdateView, self).update(request, *args, **kwargs)
        except Exception as e:
            return Response(data={'error_message': e.args}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        email = self.request.data['email']
        user = None
        try:
            user = User.objects.get(email=email)
            if user.role == User.ADMIN:
                raise Exception('Can not update Admin user')
        except ObjectDoesNotExist as e:
            e.args = ('User not found', )
            raise

        return user


class UserDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminRoleUser, ]
    serializer_class = UserSerializer  # no need serializer, for swagger added

    def delete(self, request, *args, **kwargs):
        try:
            return super(UserDeleteView, self).delete(request, *args, **kwargs)
        except Exception as e:
            return Response(data={'error_message': e.args}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        email = self.request.data['email']
        user = None
        try:
            user = User.objects.get(email=email)
            if user.role == User.ADMIN:
                raise Exception('Can not delete admin user')
        except ObjectDoesNotExist as e:
            e.args = ('User not found', )
            raise

        return user


class UserLoginView(ObtainAuthToken):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny, ]
    http_method_names = ['post', ]


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

    def get_object(self):
        team = self.request.user.team
        return team


class TeamUpdateView(generics.UpdateAPIView):
    serializer_class = TeamUpdateSerializer
    permission_classes = [IsAuthenticated, ]

    def update(self, request, *args, **kwargs):
        try:
            return super(TeamUpdateView, self).update(request, *args, **kwargs)
        except Exception as e:
            return Response(data={'error_message': e.args}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        team = None
        if self.request.user.role == User.ADMIN:
            team_id = self.request.data['id']
            try:
                team = Team.objects.get(id=team_id)
            except ObjectDoesNotExist as e:
                e.args = ('Team not found', )
                raise
        elif self.request.user.role == User.USER:
            team = self.request.user.team
            if not team:
                raise Exception('User has no team')
        return team


class PlayerUpdateView(generics.UpdateAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get_object(self):
        player = Player.objects.get(id=self.request.data['id'])
        if player not in self.request.user.team.players.all():
            return None
        return player


class SetPlayerToTransferList(views.APIView):
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        error_message = list()
        asking_price = -1
        team = request.user.team
        player = None

        if not team:
            error_message.append('User has no team')

        # get input params
        try:
            player_id = request.data['player_id']
            player = Player.objects.get(id=player_id, team=team)
        except KeyError:
            error_message.append('parameter player_id is not sent')
        except ObjectDoesNotExist:
            error_message.append('This player is not found in your team')

        try:
            asking_price = request.data['asking_price']
        except KeyError:
            error_message.append('parameter asking_price was not sent')

        if error_message:
            return Response(data={'error_message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        transfer_offer, created = TransferList.objects.get_or_create(player=player, asking_price=asking_price)
        if created:
            team.set_player_to_transfer_list(player)
            return Response(status=status.HTTP_200_OK)
        else:
            error_message.append('This player is already in Transfer List')

        return Response(data={'error_message': error_message}, status=status.HTTP_400_BAD_REQUEST)


class TransferListView(generics.ListAPIView):
    serializer_class = TransferListSerializer
    permission_classes = [IsAuthenticated, ]
    queryset = TransferList.objects.all()


class BuyTransferView(views.APIView):
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        error_message = list()
        player = None
        buying_team = request.user.team

        if not buying_team:
            error_message.append('User has no team')

        # get input params
        try:
            player_id = request.data['player_id']
            player = Player.objects.get(id=player_id)
        except KeyError:
            error_message.append('parameter player_id was not sent')
        except ObjectDoesNotExist:
            error_message.append('Player not found')

        if error_message:
            return Response(data={'error_message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        transfer_offer = player.transfer_offer
        if transfer_offer:
            try:
                transfer_offer.make_transfer(buying_team)
                return Response(status=status.HTTP_200_OK)
            except Exception as ex:
                error_message.extend(ex.args)
        else:
            error_message.append('This player is not on Transfer list')

        return Response(data={'error_message': error_message}, status=status.HTTP_400_BAD_REQUEST)
